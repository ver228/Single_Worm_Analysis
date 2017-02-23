#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 16:50:04 2017

@author: ajaver
"""

import pandas as pd
import pymysql
from sqlalchemy import create_engine

if __name__ == '__main__':
    REPLACE_PREVIOUS = False
    
    
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    cur.execute('USE `single_worm_db`;')
    
    sql = '''SELECT experiment_id, features_file
    FROM progress_analysis 
    WHERE (exit_flag_id = 
    (SELECT f.id FROM exit_flags as f WHERE checkpoint='END'))'''
    
    if REPLACE_PREVIOUS:
        cur.execute('DROP TABLE IF EXISTS features_means')
        conn.commit()
    else:
        sql += ' AND experiment_id NOT IN (SELECT experiment_id FROM features_means)' 
        
    
    cur.execute(sql)
    
    results = cur.fetchall()
    
    
    
    
    disk_engine = create_engine('mysql+pymysql:///single_worm_db')
    #%%
    def _add_to_db(data2add):
        if len(data2add) > 0:
            data2add.to_sql('features_means', 
                           disk_engine, 
                           if_exists= 'append', 
                           index = False)
    
    all_features_means = pd.DataFrame([])
    for irow, row in enumerate(results):
        print('{} of {}'.format(irow+1, len(results)))
        features_file = row['features_file']
        
        with pd.HDFStore(features_file, 'r') as fid:
            if '/features_means' in fid:
                features_means = fid['/features_means'][:]
                assert len(features_means) == 1 
                #remove unnecessary fields...
                features_means.drop(labels=['worm_index', 'n_frames', 'n_valid_skel', 'first_frame'], axis=1)
                #... and add the experiment_id 
                features_means.insert(0, 'experiment_id', row['experiment_id'])
                all_features_means = all_features_means.append(features_means)

        if (irow+1) % 50 == 0:
            _add_to_db(all_features_means)
            all_features_means = pd.DataFrame([])
    
    _add_to_db(all_features_means)
    
    cur.execute('ALTER TABLE features_means ADD UNIQUE (experiment_id);')
    cur.close()
    conn.commit()
            
        