#!/usr/bin/env python
# coding: utf-8

# In[7]:


from tkinter import*
import tkinter.filedialog
import tkinter.messagebox
global file_path1

import requests as rq
from lxml import etree
import re
from pandas import read_csv, DataFrame, set_option

import matplotlib.pyplot as plt 
import mpl_finance as mpf
#from mpl_finance import candlestick_ohlc
#import matplotlib.dates as mdates
from matplotlib.dates import date2num
from datetime import datetime

#import pandas as pd
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'}


# Check if is 404NOTFOUND
# If is not valid, return -1
def check_valid(test_url):
    # test_url = "https://www.cneeex.com/c/2021-07-16/491500.shtml"
    test_res = rq.get(test_url)        #Get方式获取网页数据
    test_res.encoding = 'utf-8' # 指定编码
    test_html = test_res.text
    rq.adapters.DEFAULT_RETRIES = 5
    if test_html.find('全国碳市场每日成交数据') != -1: # If valid
        return test_html
    else:
        return -1

# 创建主页爬虫函数
def getSy(url):
    response = rq.get(url, headers=HEADERS)
    tree = etree.HTML(response.text)
    t = tree.xpath('/html/body/div[5]/div/div[2]/div/div[2]/div/ul/li/a/@href')
    return t


def getOne(url):
    response = rq.get('https://www.cneeex.com'+url, headers=HEADERS)
    tree = etree.HTML(response.content.decode('utf-8'))
    t1 = tree.xpath('/html/body/div[5]/div/div[2]/div/div[2]/div/div[2]/div/p[2]//text()')
    t2 = tree.xpath('/html/body/div[5]/div/div[2]/div/div[2]/div/div[2]/div/p[3]//text()')
    return t1[0] + t2[0]

def path_finder1():
    global file_path1
    file_path1 = tkinter.filedialog.askopenfilename()
    entry1.insert(10,file_path1)
    
def drawK():
    #np.seterr(divide='ignore',invalid='ignore') # 忽略warning
    plt.rcParams['axes.unicode_minus']=False #用来正常显示负号 
    #fig = plt.figure(figsize=(20,12), dpi=100,facecolor="white") #创建fig对象

    data = read_csv(file_path1)

    for i in range(0,len(data.index)):
        data.loc[i,'今日全国碳市场碳排放配额（CEA）挂牌协议交易成交量'] = float(data['今日全国碳市场碳排放配额（CEA）挂牌协议交易成交量'][i].replace(',','')) / 1000

    #2、数据处理
    # data = data.loc[data.turnover_status=='交易']             # 剔除非交易日
    data_price = data[['日期','开盘价','最高价','最低价','收盘价','今日全国碳市场碳排放配额（CEA）挂牌协议交易成交量']]                  # 选取日期、高开低收价格、成交量数据
    data_price.set_index('日期', inplace=True)       # 将日期作为索引
    data_price = data_price.astype(float)                    # 将价格数据类型转为浮点数
    # 将日期格式转为 candlestick_ohlc 可识别的数值
    data_price['Date'] = list(map(lambda x:date2num(datetime.strptime(x,'%Y-%m-%d')),data_price.index.tolist()))

    #5、绘制成交量
    set_option('mode.chained_assignment', None)
    fig = plt.figure(figsize=(12,10))
    grid = plt.GridSpec(12, 10, wspace=0.5, hspace=0.5)
    #（1）绘制K线图
    # K线数据
    ohlc = data_price[['Date','开盘价','最高价','最低价','收盘价']]
    ohlc.loc[:,'Date'] = range(len(ohlc))     # 重新赋值横轴数据，绘制K线图无间隔
    # 绘制K线
    ax1 = fig.add_subplot(grid[0:8,0:12])   # 设置K线图的尺寸
    mpf.candlestick_ohlc(ax1, ohlc.values.tolist(), width=.7
                     , colorup='red', colordown='green')
    plt.title("",fontsize = 14)     # 设置图片标题
    plt.ylabel('Price Yuan(tCO_2)',fontsize = 14)   # 设置纵轴标题
    ax1.set_xticks([])                      # 日期标注在成交量中，故清空此处x轴刻度
    ax1.set_xticklabels([])                 # 日期标注在成交量中，故清空此处x轴 
    #（2）绘制成交量
    # 成交量数据
    data_volume = data_price[['Date','收盘价','开盘价','今日全国碳市场碳排放配额（CEA）挂牌协议交易成交量']]
    data_volume['color'] = data_volume.apply(lambda row: 1 if row['收盘价'] >= row['开盘价'] else 0, axis=1)       # 计算成交量柱状图对应的颜色，使之与K线颜色一致
    data_volume.Date = ohlc.Date
    # 绘制成交量
    ax2 = fig.add_subplot(grid[8:10,0:12])  # 设置成交量图形尺寸
    ax2.bar(data_volume.query('color==1')['Date']
            , data_volume.query('color==1')['今日全国碳市场碳排放配额（CEA）挂牌协议交易成交量']
            , color='b')                    # 绘制红色柱状图
    ax2.bar(data_volume.query('color==0')['Date']
            , data_volume.query('color==0')['今日全国碳市场碳排放配额（CEA）挂牌协议交易成交量']
            , color='b')                    # 绘制绿色柱状图
    plt.xticks(rotation=30) 
    plt.xlabel('Date',fontsize = 14)                               # 设置横轴标题
    # 修改横轴日期标注
    date_list = ohlc.index.tolist()           # 获取日期列表
    xticks_len = round(len(date_list)/(len(ax2.get_xticks())-1))      # 获取默认横轴标注的间隔
    xticks_num = range(0,len(date_list),xticks_len)                   # 生成横轴标注位置列表
    xticks_str = list(map(lambda x:date_list[int(x)],xticks_num))     # 生成正在标注日期列表
    new_xticks = []
    for x in xticks_str:
        new_xticks.append(datetime.strptime(x,'%Y-%m-%d').strftime("%Y %b %d "))
    ax2.set_xticks(xticks_num)                                        # 设置横轴标注位置
    ax2.set_xticklabels(new_xticks)                                   # 设置横轴标注日期
    ax2.set_ylabel("Volume (1,000 ton)",fontsize = 14)
    plt.show()

def process(path_finder1):
    s = rq.session()
    s.keep_alive = False
    # Get urlList
    urlList = []
    url = 'https://www.cneeex.com/qgtpfqjy/mrgk/index.shtml'
    i = 2;
    while True:
        if check_valid(url) != -1:
            urlList.append(url)
            url = 'https://www.cneeex.com/qgtpfqjy/mrgk/index_' + str(i) + '.shtml'
            print('... Getting urls from: ...')
            print(url)
            i = i + 1
        else:
            break
    #data_list = []
    #f = open("data.csv", 'a', encoding='utf-8', newline='')
    #writer = csv.writer(f)
    #writer.writerow(['日期','今日全国碳市场碳排放配额（CEA）挂牌协议交易成交量','成交额','开盘价','最高价','最低价','收盘价','收盘价较前一日','今日大宗协议交易成交量','成交额','今日全国碳排放配额（CEA）总成交量','总成交额','全国碳市场碳排放配额（CEA）累计成交量','累计成交额'])
    #header_list = ['日期','今日全国碳市场碳排放配额（CEA）挂牌协议交易成交量','成交额','开盘价','最高价','最低价','收盘价','收盘价较前一日','今日大宗协议交易成交量','成交额','今日全国碳排放配额（CEA）总成交量','总成交额','全国碳市场碳排放配额（CEA）累计成交量','累计成交额']
    #data_list.append(header_list)
    sumList = []
    #urlList = ['https://www.cneeex.com/qgtpfqjy/mrgk/index.shtml', 'https://www.cneeex.com/qgtpfqjy/mrgk/index_2.shtml','https://www.cneeex.com/qgtpfqjy/mrgk/index_3.shtml','https://www.cneeex.com/qgtpfqjy/mrgk/index_4.shtml']
    for i in urlList:
        sumList += getSy(i)
    sumList.reverse()
    sumL = []
    for i in range(len(sumList)):
        if i % 2 != 1:
            sumL.append(sumList[i])
    data = read_csv(file_path1)
    data_list = data.values.tolist()
    data_list.insert(0,list(data))
    latest_date = data.loc[data.index[-1]]['日期']
    inSumL = [x for x in sumL if latest_date in x][0]
    del sumL[0:sumL.index(inSumL)+1]
    
    #print(sumL)
    # 遍历每一条,正则提取

    for i in sumL:
        try:
            text = getOne(i)
            if '今日无大宗协议交易' in text:
                pattern = re.compile('挂牌协议交易成交量(.*?)吨，成交额(.*?)元，开盘价(.*?)元/吨，最高价(.*?)元/吨，最低价(.*?)元/吨，收盘价(.*?)元/吨，收盘价(.*?)。今日无大宗协议交易。今日全国碳排放配额（CEA）总成交量(.*?)吨，总成交额(.*?)元。截至今日，全国碳市场碳排放配额（CEA）累计成交量(.*?)吨，累计成交额(.*?)元。')
                results = re.findall(pattern, text.replace('\n', ''))
                print('... Processing ...')
                print(i)
                print(results)
                data_list.append([i[3:13]]+list(results[0][:7])+['0','0']+list(results[0][7:]))
                print(text)
            else:
                pattern = re.compile('挂牌协议交易成交量(.*?)吨，成交额(.*?)元，开盘价(.*?)元/吨，最高价(.*?)元/吨，最低价(.*?)元/吨，收盘价(.*?)元/吨，收盘价(.*?)。今日大宗协议交易成交量(.*?)吨，成交额(.*?)元。今日全国碳排放配额（CEA）总成交量(.*?)吨，总成交额(.*?)元。截至今日，全国碳市场碳排放配额（CEA）累计成交量(.*?)吨，累计成交额(.*?)元。')
                results = re.findall(pattern, text.replace('\n', ''))
                print(i)
                print(results)
                data_list.append([i[3:13]]+list(results[0]))
                print(text)
            time.sleep(0.2)
        except:
            pass
        
    print('... Saving ...')
    data_df = DataFrame(data_list)
    data_df[7]=data_df[7].str.replace('较前一日下跌','-')
    data_df[7]=data_df[7].str.replace('较前一日上涨','+')
    data_df[7]=data_df[7].str.replace('与前一日持平','0')
    data_df[7]=data_df[7].str.replace('较','')
    data_df.to_csv(path_finder1,header = 0, index = None)
    print('... Done ...')



def run():
    process(file_path1)



myWindow = Tk()

myWindow.title('Updater')


# Prevent resizing
myWindow.resizable(0,0)

Label(myWindow, text='Select Data File:').grid(row=0)

entry1=Entry(myWindow)
entry1.grid(row=0,column=1)



Button(myWindow, text='From', command=path_finder1).grid(row=0,column=2,sticky=W,padx=5,pady=5)
Button(myWindow, text='Run',command=run).grid(row=3,column=0,sticky=W,padx=5,pady=5)
Button(myWindow, text='Draw',command=drawK).grid(row=3,column=2,sticky=W,padx=5,pady=5)

myWindow.mainloop()


# In[ ]:








