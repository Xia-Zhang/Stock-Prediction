#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Xia Zhang
# Date: 2017/05/28

from snownlp import SnowNLP
import os
import sys
import ConfigParser
import numpy as np
import doc2vec as d2v

config = ConfigParser.ConfigParser()
config.read('stock.conf')

global count
count = 0

def get_count():
    global count
    return count

def split_sentences(str):
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    if len(str) == 0:
        return str
    punctuations = [',', '!', '?', ';', u'，', u'！', u'？']
    for punc in punctuations:
        str = str.replace(punc, '\n')
    return str

# title, five summary
def get_sentiments(title, text):
    global count
    result = []
    summary_num = config.getint("feature", "summary_num")

    if len(title.strip()) <= 1:
        result.append(0.0)
    else:
        result.append(SnowNLP(title).sentiments)
        count += 1

    if len(text.strip()) > 2:
        s = SnowNLP(text)
        for sub in s.summary(summary_num):
            result.append(SnowNLP(sub).sentiments)
    while(len(result) < 1 + summary_num):
        result.append(0.0)
    return result

def get_labels(upDowns_list):
    result = []
    for ud in upDowns_list:
        if float(ud) >= 0:
            result.append('1')
        else:
            result.append('0')
    return result

# date + "\t" + closingPrice + "\t" + openingPrice + "\t" + 涨跌幅(例如2.1%为2.1) + "\t" +highestPrice + "\t" + lowestPrice + "\t" + 成交量（手） + "\t" + 成交额（万）
def read_data(file_name):
    data_map = {'date':[], 'closingPrice':[], 'upDowns':[], 'volume':[]}
    with open(file_name) as fin:
        for line in fin.readlines():
            words = line.strip().split('\t')
            if len(words) != 8:
                print("Warning from line: " + line)
                continue
            data_map['date'].append(words[0])
            data_map['closingPrice'].append(words[1])
            data_map['upDowns'].append(words[3])
            data_map['volume'].append(words[6])
    return data_map

def get_features_labels(stock_name, stock_code, feature_code):
    stock_path = config.get("path", "stock_path")
    data_map = read_data(stock_path + stock_code + "." + stock_name)
    y = get_labels(data_map['upDowns'])
    X = []
    if feature_code & 0x10000:
        X = np.array(get_average_features(data_map['closingPrice']))
    if feature_code & 0x01000:
        tmpX = np.array(get_updowns_features(data_map['upDowns'], data_map['volume']))
        if len(X) == 0:
            X = tmpX
        else:
            X = np.concatenate((X, tmpX), axis=1)
    if feature_code & 0x00100:
        tmpX = np.array(get_tsa_features(stock_code))
        if len(X) == 0:
            X = tmpX
        else:
            X = np.concatenate((X, tmpX), axis=1)
    if feature_code & 0x00010:
        tmpX = np.array(get_sentiment_features(data_map['date'], stock_code))
        if len(X) == 0:
            X = tmpX
        else:
            X = np.concatenate((X, tmpX), axis=1)
    if feature_code & 0x00001:
        tmpX = np.array(get_Doc2Vec_features(data_map['date'], stock_code))
        if len(X) == 0:
            X = tmpX
        else:
            X = np.concatenate((X, tmpX), axis=1)
    return X, y

#################Feature Part#################

# the average of 1 day, 2 day, 5 day, 10 day, 30 day
# closing_price
def get_average_features(feature_list):
    avarage_days = [int(day) for day in config.get("feature", "avarage_days").split(',')]
    matrix = []
    if len(avarage_days) < 1:
        return matrix

    for index in range(len(feature_list)):
        price_sum = 0.0
        tmp_vec = []
        for i in range(1, max(avarage_days) + 1):
            if index - i < 0:
                break
            price_sum += float(feature_list[index - i])
            if i in avarage_days:
                tmp_vec.append(price_sum / (1.0 * i))
        while len(tmp_vec) < len(avarage_days):
            tmp_vec.append(0.0)
        matrix.append(tmp_vec)
    return matrix

# the previous 5 days features
def get_updowns_features(upDowns_list, volume_list):
    days_num = config.getint("feature", "updown_days_num")
    volume_num = config.getint("feature", "volume_num")
    matrix = []
    for index in range(len(upDowns_list)):
        tmp_vec = []
        for i in range(1, days_num + 1):
            if index - i  >= 0:
                tmp_vec.append(float(upDowns_list[index - i]))
            else:
                tmp_vec.append(0.0)
        for i in range(1, volume_num + 1):
            day1 = index - i - 1
            day2 = index - i
            if day1 <= 0 or float(volume_list[day1]) == 0.0:
                tmp_vec.append(0.0)
            else:
                tmp_vec.append(float((day2 - day1) / day1))
        matrix.append(tmp_vec)
    return matrix

# return matrix
def get_tsa_features(stock_code):
    tsa_path = config.get("path", "tsa_path")
    tsa_length = config.getint("feature", "tsa_length")
    file_name = tsa_path + stock_code + ".tsa"
    matrix = []
    with open(file_name) as fin:
        lines = fin.readlines()
        for line in lines:
            words = line.strip().split('\t')
            tmp_vec = []
            for w in words:
                if w == "nan":
                    tmp_vec.append(0.0)
                else:
                    tmp_vec.append(float(w))
                tmp_vec = tmp_vec[:min(len(tmp_vec), tsa_length)]
            matrix.append(tmp_vec)
    return matrix

# url + "\t" + date + "\t" + category + "\t" + title + "\t" + 对齐的股票代码 + "\t" + 新闻正文内容文本
def get_sentiment_features(date_list, stock_code):
    global count
    count = 0
    news_prefix = config.get("prefix", "news_prefix").split(',')
    matrix = []
    for news_date in date_list:
        dic = {'title' : [], 'text' : []}
        for prefix in news_prefix:
            file_name = prefix + news_date
            if os.path.exists(file_name) == False:
                continue
            with open(file_name) as fin:
                for line in fin.readlines():
                    words = line.strip().split()
                    code = words[4]
                    if stock_code != code:
                        continue
                    dic['title'].append(words[3])
                    dic['text'].append(words[5])
        title = ""
        text = ""
        if len(dic['title']) >=1:
            title = split_sentences('\n'.join(dic['title']))
        if len(dic['text']) >= 1:
            text = split_sentences('\n'.join(dic['text']))
        sentiment_vec =  get_sentiments(title, text)
        matrix.append(sentiment_vec)
    return matrix

def get_Doc2Vec_features(date_list, stock_code):
    return d2v.get_d2v_features(date_list, stock_code)

###############################################

if __name__ == '__main__':
    stock_code = "600087"
    stock_name = "退市长油"
    file_name = '../投资组合/上证A股股票价格/600087.退市长油'
    X, y = get_features_labels(stock_name, stock_code, int(0x00010))
    print(count)