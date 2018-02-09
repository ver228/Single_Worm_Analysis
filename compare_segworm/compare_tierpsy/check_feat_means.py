#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 13:55:40 2017

@author: ajaver
"""
import pymysql
import os

import tables
import pandas as pd
from tierpsy.helper.params import read_unit_conversions

if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    
    sql = '''SELECT *
    FROM experiments_valid
    ORDER BY experiment_id
    '''
    cur.execute(sql)
    all_rows = cur.fetchall()
    #%%
    bad_ids = []
    for irow, row in enumerate(all_rows):
        print(irow + 1, len(all_rows))
        
        features_file = os.path.join(row['results_dir'], row['base_name'] + '_features.hdf5')
        #%%
        read_unit_conversions(features_file)
        with tables.File(features_file,'r') as fid:
            if not '/features_summary' in fid:
                bad_ids.append(row['experiment_id'])
                print('bad')
        #%%
        
        