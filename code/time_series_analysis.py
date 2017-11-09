#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Xia Zhang
# Date: 2017/05/23
import os
import data_utils as du
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
from tqdm import tqdm
from snownlp import SnowNLP
import ConfigParser
from multiprocessing import Pool

from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
import statsmodels.tsa.stattools as st
from statsmodels.tsa.arima_model import ARMA


INTERVAL = 200
config = ConfigParser.ConfigParser()
config.read('stock.conf')

def get_filelist(path = '.'):
    return os.listdir(path)

def test_stationarity(data):
    timeseries = np.array(data)
    dftest = adfuller(timeseries, autolag='AIC')
    return dftest[1]

def get_diff_data(data, diff = 1):
    return data.diff(diff).dropna()
    #diff_data.columns = [u'Price diff']

def save_image(data, file_name):
    data.plot()
    plt.savefig('../images/' + file_name + '.png', format='png')

def save_acf_image(data, file_name):
    plot_acf(data)
    plt.savefig('../images/' + file_name + '.png', format='png')

def get_proper_order(data, d): # origin_data
    from statsmodels.tsa.arima_model import ARIMA
    pmax = int(len(data)/10)
    qmax = int(len(data)/10)
    ans_p = 0
    ans_q = 0
    ans_properModel = None
    ans_bit = 99999
    for p in range(pmax + 1):
        tmp = []
        for q in range(qmax + 1):
            try:
                tmp_ARIMA = ARIMA(data, (p, d, q)).fit()
            except:
                continue
            if tmp_ARIMA.bic < ans_bit:
                ans_p = p
                ans_q = q
                ans_properModel = tmp_ARIMA
                ans_bic = tmp_ARIMA.bic
    print("%d %d %d" % (ans_p, ans_q, d))
    return ans_p, ans_q, d, ans_properModel

def test_arma(timeseries):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        #order = st.arma_order_select_ic(timeseries, max_ar=5,max_ma=5,ic=['aic', 'bic', 'hqic'])
        model = ARMA(timeseries, (7, 2)).fit()
    return model.forecast(1)[0][0]

def check_ADF(data):
    from statsmodels.tsa.stattools import adfuller as ADF
    return ADF(data[data.columns[0]])[1]
    #返回值依次为adf、pvalue、usedlag、nobs、critical values、icbest、regresults、resstore

def check_white_noise(data):
    from statsmodels.stats.diagnostic import acorr_ljungbox
    print(u'The check_white_noise：', acorr_ljungbox(data, lags=1))
    # stat, p-value

def train_data(data, i):        # origin_data
    if i <= 1:
        return 0.0
    index_from = max(i - 1 - (INTERVAL - 1) , 0)
    diff_data = get_diff_data(data)
    diff_data = diff_data[index_from : i - 1]
    predict_diff = test_arma(diff_data)
    return predict_diff

def train_data_by_name(data, from_name, to_name):
    data_train = data[from_name: to_name]
    predict_diff = test_arma(data_train)
    return predict_diff

def test_precision(data):
    correct_num = 0
    total_num = len(data)
    train_num = int(len(data) * 0.8)

    #data = np.log(data)
    diff_data = get_diff_data(data)

    for i in tqdm(range(train_num, total_num)):
        name = data.index[i - 1]
        # from_name = data.index[max(i - INTERVAL, 1)]
        from_name = data.index[1]

        predict_ans = train_data_by_name(diff_data, from_name, name)
        old_ans = data[data.columns[0]][i] - data[data.columns[0]][i - 1]

        print("The ans is %f and %f" % (predict_ans, old_ans))
        if predict_ans * old_ans >= 0:
            correct_num += 1
    print("The time serial precision is %f" % (correct_num / (1.0 * (total_num - train_num))))


def get_prediction(train_data, p, q):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        model = ARMA(train_data, (p, q)).fit(disp=0)
    return model.forecast(1)[0][0]

def get_timeseries_feature(data, i):
    train_data = data[:i]
    if i <= 8 or check_ADF(train_data) > 0.05:
        return [0.0]*35
    result = []
    for p in range(0, 6):
        for q in range(0, 6):
            if p == 0 and q == 0:
                continue
            try:
                result.append(get_prediction(train_data, p, q))
            except Exception as e:
                result.append(0.0)
    return result

def write_timeseries_features(codename, fileOut):
    stock_path = config.get("path", "stock_path")
    path_file_name = stock_path + codename
    du.write_rows(path_file_name, codename + "_test.dat", [0, 1], ['Date', 'Price'])
    data = pd.read_table(codename + "_test.dat", index_col='Date')
    diff_data = get_diff_data(data)

    with open(fileOut, 'w') as fout:

        tmp_result = [0.0] * 35
        tmp_result = map(lambda x : str(x), tmp_result)
        fout.write('\t'.join(tmp_result) + '\n')
        fout.flush()

        for i in range(0, len(diff_data)):
            tmp_result = get_timeseries_feature(diff_data, i)
            tmp_result = map(lambda x : str(x), tmp_result)
            fout.write('\t'.join(tmp_result) + '\n')
            fout.flush()

    if os.path.exists(codename + "_test.dat"):
        os.remove(codename + "_test.dat")
    print("Timeseries Features Done!")

def get_filenames(path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            result.append(name)
    return result

def subprocess_tsa(name_list):
    tsa_path = config.get("path", "tsa_path")
    for name in name_list:
        stock_code, stock_name = name.split('.')
        write_timeseries_features(name, tsa_path + stock_code + ".tsa")

def get_all_timeseries_features():
    stock_path = config.get("path", "stock_path")
    train_path = config.get("path", "train_path")
    process_num = config.getint("para", "precesses")

    filenames = get_filenames(train_path)
    per_slice = int(len(filenames) / process_num)

    p = Pool()
    for i in range(process_num):
        if i == process_num - 1:
            p.apply_async(subprocess_tsa, args=(filenames[per_slice * i:], ))
        else:
            p.apply_async(subprocess_tsa, args=(filenames[per_slice * i: per_slice * (i + 1)], ))
    print("Waiting for all subprocesses done.")
    p.close()
    p.join()
    print("The process done.")

if __name__ == "__main__":
    #write_timeseries_features("600030.中信证券", "600030.tsa")
    #write_timeseries_features("601998.中信银行", "601998.tsa")
    #write_timeseries_features("601318.中国平安", "601318.tsa")
    get_all_timeseries_features();
    exit(0)
    du.write_rows("../投资组合/上证A股股票价格/600030.中信证券", "test.dat", [0, 1], ['Date', 'Price'])
    data = pd.read_table("test.dat", index_col='Date')
    test_precision(data)
    exit(0)
    # data = data['2013-1' : '2013-4']
    data = np.log(data)
    check_ADF(data)
    diff1_data = get_diff_data(data)
    diff1_data.columns = [u'Price diff']
    print(data.shape)
    print(diff1_data.shape)
    check_ADF(diff1_data)
    check_white_noise(diff1_data)
    save_image(diff1_data, "diff1")
    save_acf_image(data, "acf_origin")
    save_acf_image(diff1_data, "acf_diff1")
    # test_arma(diff1_data)
