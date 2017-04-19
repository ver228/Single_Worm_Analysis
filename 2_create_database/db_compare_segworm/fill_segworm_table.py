#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 12:08:52 2017

@author: ajaver
"""
import pymysql
#from scipy.io import loadmat
import numpy as np
import tables
import os

def update_row(cur, row_input):
    #%%
    names, values = zip(*list(row_input.items()))
    
    vals_str = []
    for x in values:
        if x is None:
            new_val = 'NULL'
        elif isinstance(x, str):
            new_val = '"{}"'.format(x)
        else:
            new_val = str(x)
        vals_str.append(new_val)
        
    values_str = ", ".join(vals_str)
    names_str = ", ".join("`{}`".format(x) for x in names)
    update_str = ", ".join('{}={}'.format(x, y) for x,y in zip(names,vals_str))
    
    
    sql = '''
    INSERT INTO `segworm_info` ({}) 
    VALUES ({})    
    ON DUPLICATE KEY UPDATE {}
    '''.format(names_str, values_str, update_str)
    
    cur.execute(sql)
    conn.commit()



SEGWORM_FEAT_LIST = '../../files_lists/segworm_feat_files.txt'

if __name__ == '__main__':
    DEL_PREV = True
    
    with open(SEGWORM_FEAT_LIST, 'r') as fid:
        flist = [x for x in fid.read().split('\n') if x]
     
    conn = pymysql.connect(host='localhost', db='single_worm_db')
    cur = conn.cursor()
    
    if DEL_PREV:
        'DELETE FROM segworm_info;'
    
    bad_files = []
    for ii, fullname in enumerate(flist):
        base_name = os.path.basename(fullname).replace('_features.mat', '')
        print(ii, len(flist), base_name)
        
        sql_map = '''
        SELECT  id
        FROM experiments
        WHERE base_name="{}"'''.format(base_name)
        cur.execute(sql_map)
        exp_id = cur.fetchone()
        if exp_id is not None:
            exp_id = exp_id[0]

        segworm_dict = {}
        segworm_dict['experiment_id'] = exp_id
        segworm_dict['segworm_file'] = fullname
        
        try:
            with tables.File(fullname, 'r')  as fid:
                segworm_dict['fps'] = fid.get_node('/info/video/resolution/fps')[0][0]
                segworm_dict['total_time'] = fid.get_node('/info/video/length/time')[0][0]
                segworm_dict['n_timestamps'] = fid.get_node('/info/video/length/frames')[0][0]
                n_valid_skeletons = np.sum(fid.get_node('/info/video/annotations/frames')[:,0]==1)
                segworm_dict['n_segworm_skeletons'] = int(n_valid_skeletons)
        except:
            bad_files.append(fullname)
        update_row(cur, segworm_dict)

    with open('bad_segworm_files.txt', 'w') as fid:
        fid.write('\n'.join(bad_files))

#%%

#    with open('/Users/ajaver/Documents/GitHub/single-worm-analysis/post_processing/compare_segworm/bad_segworm_files.txt', 'r') as fid:
#        bad_files = [x for x in fid.read().split('\n') if x]
#    
#    import shutil
#    import os
#    
#    for dst in bad_files:
#        src = dst.replace('/Volumes/behavgenom$/Andre/', '/Volumes/results-12-06-08/' )
#        
#        if os.path.exists(src):
#            print(src)
#            shutil.copyfile(src, dst)
#        else:
#            print('bad')
    #%%
    
        
        
    #/Volumes/results-12-06-08/Laura\ Grundy/     
#%%      



#SEGWORM_FEAT_LIST = '../files_lists/segworm_feat_files.txt'
#if __name__ == '__main__':
#    
#    with open(SEGWORM_FEAT_LIST, 'r') as fid:
#        flist = [x for x in fid.read().split('\n') if x]
#     
#    conn = pymysql.connect(host='localhost', db='single_worm_db')
#    
#    sql_map = '''
#    SELECT  id
#    FROM experiments
#    WHERE base_name IN ({})'''
#
#    experiment_id
#
#    for ii, fullname in enumerate(flist):
#        print(ii)
#        segworm_dict = {}
#        
#        info = loadmat(fullname, variable_names='info', struct_as_record=False, squeeze_me=True)
#        segworm_dict['segworm_file'] = fullname
#        segworm_dict['fps'] = info['info'].video.resolution.fps
#        segworm_dict['total_time'] = info['info'].video.length.time
#        segworm_dict['n_timestamps'] = info['info'].video.length.frames
#        segworm_dict['n_valid_skeletons'] = int(np.sum(info['info'].video.annotations.frames==1))
#        
        