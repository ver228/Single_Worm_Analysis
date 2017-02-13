#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:45:43 2017

@author: ajaver
"""


import pymysql
import random

conn = pymysql.connect(host='localhost', database='single_worm_db')
cur = conn.cursor()
sql = "select original_video from experiments_full where arena='35mm petri dish NGM agar low peptone'"
cur.execute(sql)
file_list = [x for x, in cur.fetchall()]

tot_files = len(file_list)
mid = tot_files//2
random.shuffle(file_list)

with open('vid_on_food_1.txt', 'w') as fid:
    for fname in file_list[:mid]:
        fid.write(fname + '\n')

with open('vid_on_food_2.txt', 'w') as fid:
    for fname in file_list[mid:]:
        fid.write(fname + '\n')