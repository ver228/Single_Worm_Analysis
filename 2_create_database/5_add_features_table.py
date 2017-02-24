#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 16:50:04 2017

@author: ajaver
"""
import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine

if __name__ == '__main__':
    REPLACE_PREVIOUS = False
    
    
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    cur.execute('USE `single_worm_db`;')
    
    sql = '''SELECT id, results_dir, base_name
    FROM experiments 
    WHERE exit_flag_id > 
    (SELECT f.id FROM exit_flags as f WHERE name='FEAT_CREATE')
    AND exit_flag_id <100'''
    
    if REPLACE_PREVIOUS:
        cur.execute('DROP TABLE IF EXISTS features_means')
        conn.commit()
    else:
        sql += ' AND id NOT IN (SELECT experiment_id FROM features_means)' 
        
    
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
    
    for irow, row in enumerate(results):
        print('{} of {}'.format(irow+1, len(results)))
        features_file = os.path.join(row['results_dir'], row['base_name'] + '_features.hdf5')
        
        with pd.HDFStore(features_file, 'r') as fid:
            if '/features_means' in fid:
                features_means = fid['/features_means'][:]
                assert len(features_means) == 1 
                #remove unnecessary fields...
                features_means.drop(labels=['worm_index', 'n_frames', 'n_valid_skel', 'first_frame'], axis=1)
                #... and add the experiment_id 
                features_means.insert(0, 'experiment_id', row['id'])
                
        _add_to_db(features_means)
        
    
    #modify table for some reason the default of int would be bigint
    sql = '''
    ALTER TABLE features_means
    MODIFY experiment_id INT
    '''
    cur.execute(sql)
    sql = '''
    ALTER TABLE features_means
    ADD FOREIGN KEY (`experiment_id`) REFERENCES `experiments`(`id`)
    '''
    cur.execute(sql)
    
    
    cur.close()
    conn.commit()
            
        