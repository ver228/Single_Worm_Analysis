#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 12:12:49 2017

@author: ajaver
"""

import pymysql
import pandas as pd
import matplotlib.pylab as plt
import numpy as np

conn = pymysql.connect(host='localhost', db='single_worm_db')
cur = conn.cursor()
sql = '''
SELECT id, base_name, original_video_sizeMB, n_valid_frames, mask_file_sizeMB, total_time, fps
FROM experiments 
JOIN results_summary ON id = experiment_id
'''
results = pd.read_sql(sql, con=conn)  
results = results[results['original_video_sizeMB']>1]


results['compression_ratio'] = results['original_video_sizeMB']/results['mask_file_sizeMB']


xx = results['n_valid_frames']
yy = results['mask_file_sizeMB']
plt.plot(xx, yy, '.')

xx = results['n_valid_frames']
yy = results['original_video_sizeMB']
plt.plot(xx, yy, '.r')