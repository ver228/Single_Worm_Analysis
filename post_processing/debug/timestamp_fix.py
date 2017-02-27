#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 18:29:24 2017

@author: ajaver
"""

import os
import tables
import numpy as np
#import pymysql
import multiprocessing as mp

#from tierpsy.analysis.stage_aligment.alignStageMotion import alignStageMotion
from tierpsy.analysis.compress.extractMetaData import _correct_timestamp

def correct_timestamp_files(input_dat):
    exp_id, base_name, original_video, results_dir = input_dat
    mask_file = os.path.join(results_dir, base_name + '.hdf5')
    skel_file = os.path.join(results_dir, base_name + '_skeletons.hdf5')
    print(exp_id+1)
    
    out = _read_timestamps(mask_file)
    if out is None:
        return exp_id
    
    _timestamp, _timestamp_time = out
    def _replace_timestamp(fname):
        with tables.File(fname, 'r+') as fid:
            if '/timestamp' in fid:
                fid.remove_node('/timestamp', recursive=True)
            fid.create_array('/timestamp', 'raw', obj=_timestamp ,createparents=True)
            fid.create_array('/timestamp', 'time', obj=_timestamp_time ,createparents=True)
    
    for fname in [mask_file, skel_file]:
        _replace_timestamp(fname)
        
    with tables.File(skel_file, 'r+') as fid:
        tab = fid.get_node('/trajectories_data')
        frame_number_t = tab.col('frame_number')
        timestamp_raw_t = _timestamp[frame_number_t]
        timestamp_time_t = _timestamp_time[frame_number_t]
        
        for ii, row in enumerate(tab):
            row['timestamp_raw'] = timestamp_raw_t[ii]
            row['timestamp_time'] = timestamp_time_t[ii]
            row.update()
        tab.flush()
        
    #alignStageMotion(mask_file, skel_file)
    
    return exp_id, len(frame_number_t)

def _read_timestamps(mask_file):
    
    if not os.path.exists(mask_file):
        return None
    
    with tables.File(mask_file, 'r') as mask_fid:
        if '/video_metadata' in mask_fid:
            dd = [(row['best_effort_timestamp'], row['best_effort_timestamp_time'])
                          for row in mask_fid.get_node('/video_metadata/')]
            best_effort_timestamp, best_effort_timestamp_time = list(map(np.asarray, zip(*dd)))
            best_effort_timestamp = best_effort_timestamp.astype(np.int)
            
            timestamp, timestamp_time = \
            _correct_timestamp(best_effort_timestamp, best_effort_timestamp_time)
            
            return timestamp, timestamp_time
        else:
            return None
        
def correct_data(input_dat):
    correct_timestamp_files(input_dat)
    exp_id, base_name, original_video, results_dir = input_dat
    
    print(exp_id, len(results), base_name)
    #mask_file = os.path.join(results_dir, base_name + '.hdf5')
    skel_file = os.path.join(results_dir, base_name + '_skeletons.hdf5')
    if os.path.exists(skel_file):
        with tables.File(skel_file, 'r+') as fid:
            if '/provenance_tracking/STAGE_ALIGMENT' in fid:
                fid.remove_node('/provenance_tracking/STAGE_ALIGMENT')
                 

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
    all_timestamps = []
    n = 100
    for i in range(0, len(results), n):
        dat = results[i:i + n]
        res = list(p.imap(correct_data, dat))
        all_timestamps.append(res)
    
#    import glob
#    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
#    f_list = glob.glob(os.path.join(main_dir, '*_features.mat'))
#    
#    base_names = [os.path.basename(x).replace('_features.mat', '') for x in f_list]
#    results_dir = [os.path.dirname(x) for x in f_list]
#    
#    results = [(0, x, '', y) for x,y in zip(base_names, results_dir)]
#    for input_dat in results:
#        correct_data(input_dat)
    
    #%%    
#    with open("missing.txt", 'w') as fid:
#        fid.write('\n'.join(files2process))
        