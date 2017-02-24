#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 18:29:24 2017

@author: ajaver
"""

import pymysql
import os
import tables
import numpy as np
import multiprocessing as mp

def read_timestamps_test(input_dat):
    #%%
    exp_id, base_name, original_video, results_dir = input_dat
    
    mask_file = os.path.join(results_dir, base_name + '.hdf5')
    
    if not os.path.exists(mask_file):
        return (exp_id)
    
    print(exp_id+1, len(results))
    with tables.File(mask_file, 'r') as mask_fid:
        tot_masks = mask_fid.get_node('/mask').shape[0]
        
        if '/video_metadata' in mask_fid and tot_masks > 1:
            dd = [(row['best_effort_timestamp'], row['best_effort_timestamp_time'])
                          for row in mask_fid.get_node('/video_metadata/')]
            best_effort_timestamp, best_effort_timestamp_time = list(map(np.asarray, zip(*dd)))
            timestamp, timestamp_time = best_effort_timestamp.astype(np.int), best_effort_timestamp_time
            
            deli = np.diff(timestamp)
            delt = np.diff(timestamp_time)
            good = deli>0
            
            deli_min = np.min(deli[good])
            delt_min = np.min(delt[good])
                #%%
            if deli_min != 1:
                return (exp_id, tot_masks, deli_min, delt_min, timestamp, timestamp_time)
            else:
                return (exp_id, tot_masks, deli_min, delt_min)
            
            
        else:
            return (exp_id, tot_masks)
        
if __name__ == '__main__':
    
    conn = pymysql.connect(host='localhost', db = 'single_worm_db')
    cur = conn.cursor()
    sql = '''
    SELECT id, base_name, original_video, results_dir
    FROM experiments_full
    '''
    cur.execute(sql)
    results = cur.fetchall()
    
    
    p = mp.Pool(20)
    
    all_timestamps_d = []
    n = 100
    for i in range(0, len(results), n):
        dat = results[i:i + n]
        input_dat = list(p.imap(read_timestamps_test, dat))
        all_timestamps_d.append(input_dat)
        
    #%%
#    all_timestamps = []
#    for i in range(9900, 10000):
#        input_dat = read_timestamps_test(results[i])
#        all_timestamps.append(input_dat)
        
    
        
    #%%
    all_timestamps = sum(all_timestamps_d, [])
    dd = [x for x in all_timestamps if not isinstance(x, int) and len(x) > 2 and x[2]!=1]

