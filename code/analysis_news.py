#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Xia Zhang
# Date: 2017/05/28

from snownlp import SnowNLP

def split_sentences(str):
    punctuations = [',', '!', '?', '', u'，', u'！', u'？']
    for punc in punctuations:
        str.replace(punc, '\n')
    return str

# title, five summary
def get_sentiments(title, text):
    result = []
    result.append(SnowNLP(title).sentiments)
    if len(result) == 0:
        result.append(0.0)
    s = SnowNLP(text)
    for sub in s.summary(5):
        result.append(SnowNLP(sub).sentiments)
    while(len(result) < 6):
        result.append(0.0)
    return result

# url + "\t" + date + "\t" + category + "\t" + title + "\t" + 对齐的股票代码 + "\t" + 新闻正文内容文本
def get_news_features(news_date, stock_code):
    path = "../code/投资组合/上证A股相关新闻及研究报告/alignedArticles/crr_" 
    file_name = path + news_date
    dic = {'title' : [], 'text' : []}
    with open(file_name) as fin:
        for line in fin.readlines():
            words = line.strip().split()
            code = words[4]
            if stock_code != code:
                continue
            dic['title'].append(words[3])
            dic['text'].append(words[5])
    title = split_sentences('\n',join(dic['title']))
    text = split_sentences('\n'.join(dic['text']))

# date + "\t" + closingPrice + "\t" + openingPrice + "\t" + 涨跌幅(例如2.1%为2.1) + "\t" +highestPrice + "\t" + lowestPrice + "\t" + 成交量（手） + "\t" + 成交额（万）
def get_features(stock_code, data_map, index):
    result = get_news_features(data_map['date'][index], stock_code)
    result.extend(get_average_features(data_map['closingPrice'][index]))
    return result

def get_features_matrix(file):
    pass

def read_data(file_name):
    data_map = {'date':[], 'closingPrice':[], 'upDowns':[], ''}
    with open(file_name) as fin:
        for line in fin.readlines():
            words = line.strip().split('\t')

