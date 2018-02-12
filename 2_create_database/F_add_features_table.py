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
import multiprocessing as mp

from tierpsy.helper.misc import TimeCounter

if __name__ == '__main__':
    REPLACE_PREVIOUS = True
    
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
    
    all_rows = cur.fetchall()
    
    disk_engine = create_engine('mysql+pymysql:///single_worm_db')
    #%%
    def _add_to_db(data2add):
        if len(data2add) > 0:
            data2add.to_sql('features_means', 
                           disk_engine, 
                           if_exists= 'append', 
                           index = False)
    def _process_row(row):
       features_file = os.path.join(row['results_dir'], row['base_name'] + '_features.hdf5')
       with pd.HDFStore(features_file, 'r') as fid:
            if '/features_summary/means' in fid:
                features_means = fid['/features_summary/means'][:]
                assert len(features_means) == 1 
                #remove unnecessary fields...
                features_means.drop(labels=['worm_index', 'n_frames', 'n_valid_skel', 'first_frame'], axis=1)
                #... and add the experiment_id 
                features_means.insert(0, 'experiment_id', row['id'])
                
                return features_means
            
        
    
    print('*******', len(all_rows))
    progress_timer = TimeCounter()
    
    n_batch = mp.cpu_count()
    p = mp.Pool(n_batch)
    tot = len(all_rows)
    for ii in range(0, tot, n_batch):
        dat = all_rows[ii:ii + n_batch]       
        features_means = [x for x in p.map(_process_row, dat) if x is not None]
        if features_means:
            features_means = pd.concat(features_means)
            _add_to_db(features_means)
            
        print('{} of {}. Total time: {}'.format(min(tot, ii + n_batch),
                  tot, progress_timer.get_time_str()))
        
    #%%
    #modify table for some reason the default of int would be bigint
    sql = '''
    ALTER TABLE features_means
    MODIFY experiment_id INT;
    '''
    cur.execute(sql)
    #%% REMOVE ANY DUPLICATED KEYS
    sql = '''
    DROP TABLE IF EXISTS tmp;
    CREATE TABLE tmp LIKE `features_means`;
    '''
    cur.execute(sql)
    
    #add constraint if it doesn't exists
    n = cur.execute("SHOW KEYS FROM tmp WHERE Key_name='u_experiment_id';")
    if n == 0:
        cur.execute("ALTER TABLE tmp ADD CONSTRAINT `u_experiment_id` UNIQUE(`experiment_id`);")

    
    sql = '''
    INSERT IGNORE INTO tmp SELECT * FROM `features_means`;
    RENAME TABLE `features_means` TO deleteme, tmp TO `features_means`;
    DROP TABLE deleteme;
    '''
    cur.execute(sql)
    
    
    #%%

    #ADD FOREING KEY CONSTRAIN
    n = cur.execute("SELECT * FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_NAME = 'features_means_ibfk_1';")
    if n == 0:
        sql = '''
        ALTER TABLE features_means
        ADD CONSTRAINT `features_means_ibfk_1` 
        FOREIGN KEY (`experiment_id`) REFERENCES `experiments`(`id`);
        '''
        cur.execute(sql)
    #%%
    cur.close()
    conn.commit()
       
        