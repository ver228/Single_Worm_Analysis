#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 10:50:07 2017

@author: ajaver
"""

import glob
import os
import pymysql
import shutil

from tierpsy.analysis.compress_add_data.getAdditionalData import getAdditionalFiles

if __name__ == '__main__':
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    
    flist = glob.glob(os.path.join(main_dir, '*_features.mat'))
    base_names = [os.path.basename(x).replace('_features.mat', '') for x in flist]
    
    conn = pymysql.connect(host='localhost', db='single_worm_db')
    cur = conn.cursor()
    
    sql = '''
    SELECT original_video
    FROM experiments
    WHERE base_name IN ({})
    '''.format(','.join(['"' + x + '"' for x in base_names]))
    cur.execute(sql)
    results = cur.fetchall()
    
    save_dir = '/Volumes/behavgenom_archive$/single_worm/segworm_test'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    for video_file, in results:
        info_file, stage_file = getAdditionalFiles(video_file)
        for fname in [video_file, info_file, stage_file]:
            shutil.copy(fname, save_dir)