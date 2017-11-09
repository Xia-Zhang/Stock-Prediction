#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Xia Zhang
# Date: 2017/05/29

import get_features as gf
from sklearn import svm
import ConfigParser
import datetime
import os

config = ConfigParser.ConfigParser()
config.read('stock.conf')

def get_precision(Y, predict_Y):
    n = len(Y)
    count = 0
    for i in range(len(Y)):
        if Y[i] == predict_Y[i]:
            count += 1
    return (count / (1.0 * n))

def model(stock_name, stock_code, feature_code):
    X, y = gf.get_features_labels(stock_name, stock_code, feature_code)
    train_n = int(0.8 * len(y))
    train_X, train_y =  X[:train_n], y[:train_n]
    clf = svm.SVC()
    clf.fit(train_X, train_y)
    predict_y = clf.predict(X[train_n:])
    return get_precision(y[train_n:], predict_y)

def get_filenames(path):
    for root, dirs, files in os.walk(path):
        return files

def write_title():
    output = config.get("file", "output")
    with open(output, "a") as fout:
        now = datetime.datetime.now()
        fout.write('\n' + now.strftime('%Y-%m-%d %H:%M:%S') + '\n')
        fout.write("Name\tAverage\tPreviousN\tTSA\tSentiment\tDoc2Vec\tDataAll\tNewsALL\tALL\tCount\n")

def get_train_result():
    stock_path = config.get("path", "stock_path")
    train_path = config.get("path", "train_path")
    feature_codes = [0x10000, 0x01000, 0x00100, 0x00010, 0x00001, 0x11100, 0x00011, 0x11111]
    filenames = get_filenames(train_path)
    #filenames = ["600087.退市长油", "600030.中信证券", "601318.中国平安", "601998.中信银行"]
    output = config.get("file", "output")
    write_title()
    with open(output, "a") as fout:
        for name in filenames:
            stock_code, stock_name = name.split('.')
            fout.write(name + "\t")
            for feature_code in feature_codes:
                fout.write(str(model(stock_name, stock_code, feature_code)) + "\t")
            fout.write(str(gf.get_count()) + '\n')
            fout.flush()

if __name__ == '__main__':
    get_train_result()
