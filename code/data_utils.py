#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Xia Zhang
# Date: 2017/05/23

def write_row(fileIn, fileOut, num):
    with open(fileIn) as fin, open(fileOut, 'w') as fout:
        for line in fin.readlines():
            words = line.strip().split('\t')
            if len(words) <= num:
                print("Not enough rows in %s!" % line)
                exit(0)
            fout.write(words[num] + "\n")

def write_rows(fileIn, fileOut, nums, names = []):
    with open(fileIn) as fin, open(fileOut, 'w') as fout:
        if len(names) != 0:
            for i in range(len(names)):
                if i != len(names) - 1:
                    fout.write(names[i] + '\t')
                else:
                    fout.write(names[i] + '\n')
        for line in fin.readlines():
            words = line.strip().split('\t')
            for i in range(len(nums)):
                if len(words) <= nums[i]:
                    print("Not enough %d rows in %s!" % (nums[i], line))
                    exit(0)
                fout.write(words[nums[i]])
                if i != len(nums) - 1:
                    fout.write('\t')
                else:
                    fout.write('\n')

def get_rows(fileIn, nums):
    result = []
    with open(fileIn) as fin:
        for line in fin.readlines():
            tmp_line = []
            words = line.strip().split('\t')
            for i in range(len(nums)):
                if len(words) <= nums[i]:
                    print("Not enough %d rows in %s!" % (nums[i], line))
                    exit(0)
                tmp_line.append(words[nums[i]])    
    return result

def read_data_list(fileIn):
    result = []
    with opne(fileIn) as fin:
        for line in fin.readlines:
            tmp_line = line.strip().split('\t')
            ans.append(tmp_line)
    return result


if __name__ == "__main__":
    pass