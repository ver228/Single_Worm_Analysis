#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 16:29:28 2017

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
        
    segworm_basenames = set(_get_basename(x) for x in flist if x)
    
    
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute('USE `single_worm_db`;')
    
    sql = '''
        SELECT e.id, e.base_name, e.original_video, e.arena_id
        FROM analysis_progress AS a
        JOIN experiments AS e ON e.id = a.experiment_id
        JOIN exit_flags AS f ON f.id = a.exit_flag_id
        WHERE f.checkpoint="FAIL_STAGE_ALIGMENT"
        '''
    
    cur.execute(sql)
    unaligned_rows = cur.fetchall()
    unaligned_map = {x['base_name']:x['original_video'] for x in unaligned_rows}
    unaligned_basenames = set(unaligned_map.keys())
    
    
    swim_bn = set(x['base_name'] for x in unaligned_rows if x['arena_id'] == 2)
    segworm_unalgined_bn = segworm_basenames.intersection(unaligned_basenames)
    rest_bn = unaligned_basenames.difference(segworm_unalgined_bn).difference(swim_bn)
    
    assert (len(swim_bn)+len(segworm_unalgined_bn)+len(rest_bn)) == len(unaligned_basenames)
    
    
    dat_pairs = [
            ('swimming.txt', swim_bn),
            ('aligned_in_old_db.txt',segworm_unalgined_bn),
            ('missing_in_old_db.txt',rest_bn)
            ]
    
    for fname, basenames in dat_pairs:
        flist = [unaligned_map[bn].replace('thecus', 'MaskedVideos').replace('.avi', '.hdf5') for bn in basenames]
        assert all([os.path.exists(x) for x in flist])
        
        with open(fname, 'w') as fid:
            fid.write('\n'.join(flist))
        
        
        
    