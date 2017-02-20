#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 14:54:04 2017

@author: ajaver
"""

import pymysql
import os

SEGWORM_FEAT_LIST = '../files_lists/segworm_feat_files.txt'

if __name__ == '__main__':
    def _get_basename(x):
        return os.path.basename(x).replace('_features.mat', '')
    with open(SEGWORM_FEAT_LIST, 'r') as fid:
        flist = fid.read().split('\n')
        
        key_basenames = {_get_basename(x):x for x in flist if x}
    
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute('USE `single_worm_db`;')
    
    segworm_basenames = list(key_basenames.keys())
    
    sql_map = '''
    SELECT id, base_name
    FROM experiments
    WHERE base_name IN ({})
    '''.format(','.join('"' + x + '"' for x in segworm_basenames))
    cur.execute(sql_map)
    results = cur.fetchall()
    segworm_db_mapper = {x['id']:key_basenames[x['base_name']] for x in results}
    
    print('Missing previously analyzed files {}'.format(len(segworm_basenames) - len(results)))
    
    #%%
    sql_finished = '''
    SELECT e.id, a.features_file, a.exit_flag_id
    FROM experiments AS e
    JOIN analysis_progress AS a ON e.id = a.experiment_id
    WHERE exit_flag_id >= (SELECT f.id FROM exit_flags as f WHERE checkpoint="WCON_EXPORT")
    AND exit_flag_id < 100
    '''
    cur.execute(sql_finished)
    results = cur.fetchall()
    #%%
    
    feat_files = [(segworm_db_mapper[x['id']], x['features_file']) 
    for x in results if x['id'] in segworm_db_mapper]
    
    
    
    #%%
    
    

    



#sql_liquid = '''
#select original_video 
#from experiments_full 
#where arena like '%liquid%' order by original_video_sizeMB DESC'''
#
#
#sql_agar = '''
#select original_video 
#from experiments_full 
#where arena not like '%liquid%'
#order by original_video_sizeMB DESC'''