#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Xia Zhang
# Date: 2017/05/28

from snownlp import SnowNLP
import os
import sys


global count
global AVARAGE_DAYS, SUMMARY_SENTIMENTS, TIME_SERIES
count = 0

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
    global SUMMARY_SENTIMENTS

    result = []
    if len(title) <= 1:
        result.append(0.0)
    else:
        result.append(SnowNLP(title).sentiments)
        count += 1
    if len(text.strip()) > 2:
        s = SnowNLP(text)
        for sub in s.summary(SUMMARY_SENTIMENTS):
            result.append(SnowNLP(sub).sentiments)
    while(len(result) < 1 + SUMMARY_SENTIMENTS):
        result.append(0.0)
    return result

# url + "\t" + date + "\t" + category + "\t" + title + "\t" + 对齐的股票代码 + "\t" + 新闻正文内容文本
def get_news_features(news_date, stock_code):
    paths = ["../投资组合/上证A股相关新闻及研究报告/alignedArticles/crr_", "../投资组合/上证A股相关新闻及研究报告/alignedArticles/news_"]
    dic = {'title' : [], 'text' : []}
    for path in paths:
        file_name = path + news_date
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
    return get_sentiments(title, text)

# the average of 1 day, 2 day, 5 day, 10 day, 30 day
def get_average_features(feature_list, index):
    global AVARAGE_DAYS
    related_days = AVARAGE_DAYS
    if len(related_days) < 1:
        return []
    result = []
    related_days = set(related_days)
    price_sum = 0.0
    for i in range(1, min(AVARAGE_DAYS[len(related_days) - 1], len(feature_list))):
        price_sum += float(feature_list[i])
        if i in related_days:
            result.append(price_sum / (1.0 * i))
    while len(result) < len(related_days):
        result.append(0.0)
    return result

def get_updowns_features(upDowns_list, index):
    result = []
    for i in range(1, 6):
        if index - i  >= 0:
            result.append(float(upDowns_list[index - i]))
        else:
            result.append(0.0)
    return result

# date + "\t" + closingPrice + "\t" + openingPrice + "\t" + 涨跌幅(例如2.1%为2.1) + "\t" +highestPrice + "\t" + lowestPrice + "\t" + 成交量（手） + "\t" + 成交额（万）
def get_features(stock_code, data_map, index):
    result = get_news_features(data_map['date'][index], stock_code)
    result.extend(get_average_features(data_map['closingPrice'], index))
    result.extend(get_updowns_features(data_map['upDowns'], index))
    return result

def get_labels(upDowns_list):
    result = []
    for ud in upDowns_list:
        if float(ud) >= 0:
            result.append('1')
        else:
            result.append('0')
    return result

def get_features_matrix(file_name, stock_code):
    features_matrix = []
    data_map = read_data(file_name)
    labels = get_labels(data_map['upDowns'])
    n = len(labels)
    for i in range(n):
        features_matrix.append(get_features(stock_code, data_map, i))
    return features_matrix, labels

def set_global_parameters(avarage_days, summary_sentiments, time_series):
    global AVARAGE_DAYS, SUMMARY_SENTIMENTS, TIME_SERIES
    AVARAGE_DAYS = avarage_days
    SUMMARY_SENTIMENTS = summary_sentiments
    TIME_SERIES = time_series

def get_sentiments_matrix(file_name):
    global TIME_SERIES
    result = []
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
                tmp_vec = tmp_vec[:min(len(tmp_vec), TIME_SERIES)]
            result.append(tmp_vec)
    return result

def get_combine_features_matrix(file_name, stock_code, avarage_days = [1, 2, 5, 10, 30], summary_sentiments = 5, time_series = 35):
    set_global_parameters(avarage_days, summary_sentiments, time_series)
    features_matrix = []
    data_map = read_data(file_name)
    labels = get_labels(data_map['upDowns'])
    n = len(labels)
    sentiments_matrix = get_sentiments_matrix(stock_code + ".tsa")
    for i in range(n):
        tmp_features = get_features(stock_code, data_map, i)
        tmp_features.extend(sentiments_matrix[i])
        features_matrix.append(tmp_features)
    return features_matrix, labels

def read_data(file_name):
    data_map = {'date':[], 'closingPrice':[], 'upDowns':[]}
    with open(file_name) as fin:
        for line in fin.readlines():
            words = line.strip().split('\t')
            if len(words) != 8:
                print("Warning from line: " + line)
                continue
            data_map['date'].append(words[0])
            data_map['closingPrice'].append(words[1])
            data_map['upDowns'].append(words[3])
    return data_map

if __name__ == '__main__':
    stock_code = "600030"
    file_name = '../投资组合/上证A股股票价格/' + stock_code + ".中信证券"
    X, y = get_features_matrix(file_name, stock_code)
    print(count)