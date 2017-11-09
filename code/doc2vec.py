#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Xia Zhang
# Date: 2017/06/03

import ConfigParser
import threading
import os
import sys
import jieba
import multiprocessing
import gensim
from tqdm import tqdm


config = ConfigParser.ConfigParser()
config.read('stock.conf')

class myThread(threading.Thread):
    def __init__(self, threadID, nameList):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.nameList = nameList

    def run(self):
        print("Thread %s start running" % self.threadID);
        stock_path = config.get("path", "stock_path")
        news_path = config.get("path", "news_path")
        doc2vec_path = config.get("path", "doc2vec_path")
        news_prefix = config.get("prefix", "news_prefix").split(',')
        file_out = doc2vec_path + str(self.threadID) + ".d2v"
        for name in self.nameList:
            fileIn = stock_path + name;
            stock_code, stock_name = name.split('.')
            with open(fileIn) as fin:
                lines = fin.readlines()
                for line in lines:
                    words = line.split('\t')
                    stock_date = words[0]
                    stock_updown = 1 if float(words[3]) > 0 else 0
                    news_text_list = self.get_news_text(stock_date, stock_code)
                    for text in news_text_list:
                        self.write_text_label(file_out, text, stock_updown)

    def get_news_text(self, stock_date, stock_code):
        news_prefix = config.get("prefix", "news_prefix").split(',')
        text_list = []
        for prefix in news_prefix:
            file_name = prefix + stock_date
            if os.path.exists(file_name) == False:
                continue
            else:
                with open(file_name) as fin:
                    for line in fin.readlines():
                        words = line.strip().split('\t')
                        code = words[4]
                        if stock_code != code:
                            continue
                        else:
                            text_list.append(clean_text(words[5]))
        return text_list

    def write_text_label(self, file_out, text, label):
        with open(file_out, 'a') as fout:
            fout.write("%s\t%d\n" % (text, label))

def get_news_text_by_date(stock_date, stock_code):
    news_prefix = config.get("prefix", "news_prefix").split(',')
    text_list = ""
    for prefix in news_prefix:
        file_name = prefix + stock_date
        if os.path.exists(file_name) == False:
            continue
        else:
            with open(file_name) as fin:
                for line in fin.readlines():
                    words = line.strip().split('\t')
                    code = words[4]
                    if stock_code != code:
                        continue
                    else:
                        text_list += clean_text(words[5])
    return text_list

def write_text(file_in, file_out):
    with open(file_in) as fin, open(file_out, 'a') as fout:
        for line in fin:
            words = line.strip().split('\t')
            text = clean_text(words[5])
            fout.write(text + "\n")

def clean_text(text):
    stopwords_file = config.get("file", "stopwords_list")
    stopwords_list = [word.strip() for word in open(stopwords_file).readlines()]
    segs = jieba.cut(text, cut_all=False)
    segs = [word for word in segs if word not in stopwords_list]
    return " ".join(segs)


def function():
    stock_path = config.get("path", "stock_path")
    news_path = config.get("path", "news_path")
    for root, dirs, files in os.walk(train_path):
        for name in files:
            stock_code, stock_name = name.split('.')

def get_filenames(path):
    for root, dirs, files in os.walk(path):
        return files
    ## The recursive version
    # result = []
    # for root, dirs, files in os.walk(path):
    #     for name in files:
    #         result.append(name)
    # return result

def write_doc2vec_file():
    thread_num = config.getint("para", "threads")
    stock_path = config.get("path", "stock_path")
    pool = []
    filenames = get_filenames(stock_path)
    per_slice = int(len(filenames) / thread_num)
    for i in range(thread_num):
        if i == thread_num - 1:
            mythread = myThread(i, filenames[per_slice * i:])
        else:
            mythread = myThread(i, filenames[per_slice * i: per_slice * (i + 1)])
        mythread.start()
        pool.append(mythread)
    for p in pool:
        p.join()
    print("The write is done")

def write_doc2vec_corpus():
    news_path = config.get("path", "news_path")
    file_corpus = config.get("file", "corpus")
    filenames = get_filenames(news_path)
    for name in tqdm(filenames):
        write_text(news_path + name, file_corpus)
    print("The write is done!")

def train_model():
    file_corpus = config.get("file", "mini_corpus")
    epoch = config.getint("para", "epoch")
    model_file = config.get("file", "model_file")
    sentences = gensim.models.doc2vec.TaggedLineDocument(file_corpus)
    model = gensim.models.Doc2Vec(sentences, size = 100, window = 5, alpha = 0.015)
    model.save(model_file)
    print("Model is done!")

def get_d2v_features(date_list, stock_code):
    matrix = []
    model_file = config.get("file", "model_file")
    model = gensim.models.Doc2Vec.load(model_file)
    for date in date_list:
        text = get_news_text_by_date(date, stock_code)
        tmp_vec = []
        if len(text) <= 1:
            tmp_vec = [0.0] * 100
        else:
            tmp_vec = model.infer_vector(text)
        matrix.append(tmp_vec)
    return matrix

if __name__ == "__main__":

    train_model()