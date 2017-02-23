#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 14:54:04 2017

@author: ajaver
"""

import pymysql
import os

def export_rand_sample(f_list, mat_mapper):
    import random
    import shutil
    
    save_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3'
    sample_bn = random.sample(f_list, 50)
    
    sql_sample = '''
    SELECT  e.id, e.original_video
    FROM experiments AS e
    WHERE base_name IN ({})
    '''.format(','.join('"' + x + '"' for x in sample_bn))
    
    cur2= conn.cursor()
    cur2.execute(sql_sample)
    results = cur2.fetchall()
    
    for exp_id, original_video in results:
        print(exp_id)
        
        mask_file = original_video.replace('thecus', 'MaskedVideos').replace('.avi', '.hdf5')
        skel_file = original_video.replace('thecus', 'Results').replace('.avi', '_skeletons.hdf5')
        feat_file = original_video.replace('thecus', 'Results').replace('.avi', '_features.hdf5')
        
        fnames = [mask_file, skel_file, feat_file, mat_mapper[exp_id]]
        
        for fname in fnames:
            assert os.path.exists(fname)
            print(fname)
            shutil.copy(fname, save_dir)

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
    SELECT  e.id, e.base_name, a.features_file, f.checkpoint
    FROM experiments AS e
    JOIN analysis_progress AS a ON e.id = a.experiment_id
    JOIN exit_flags AS f ON f.id = a.exit_flag_id
    WHERE base_name IN ({})
    '''.format(','.join('"' + x + '"' for x in segworm_basenames))
    cur.execute(sql_map)
    results = cur.fetchall()
    segworm_db_mapper = {x['id']:key_basenames[x['base_name']] for x in results}
    
    print('Missing previously analyzed files {}'.format(len(segworm_basenames) - len(results)))
    
    #%%
    group_by_point = {}
    for row in results:
        if not row['checkpoint'] in group_by_point:
            group_by_point[row['checkpoint']] = []
        
        group_by_point[row['checkpoint']].append(row['base_name'])
    #%%
    print({x:len(val) for x,val in group_by_point.items()})
    #%%
    export_rand_sample(group_by_point['WCON_EXPORT'], segworm_db_mapper)
    
    
    
    
    
    
    
 #%%
   