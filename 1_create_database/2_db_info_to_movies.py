#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 16:59:45 2017

@author: ajaver
"""
import os
import json
import tables
import pymysql.cursors
from collections import OrderedDict

from tierpsy.processing.batchProcHelperFunc import walkAndFindValidFiles

def db_row2dict(row):
    
    experiment_info = OrderedDict()
    experiment_info['base_name'] = row['base_name']
    
    if not 'experimenter' in row:
        experiment_info['who'] = 'Laura Grundy'
    else:
        experiment_info['who'] = row['experimenter']
    
    if not 'lab' in row:
        #I hard code the lab for the moment since all this data base is for the single worm case, and all the data was taken from the schafer lab.
        #if at certain point we add another lab we need to add an extra table in the main database
        experiment_info['lab'] = {'name' : 'William R Schafer', 
        'address':'MRC Laboratory of Molecular Biology, Hills Road, Cambridge, CB2 0QH, UK'}
    else:
        experiment_info['lab'] = row['lab']
        
    experiment_info['timestamp'] = row['date'].isoformat()
    
    
    
    experiment_info['arena'] = {
            "kind":'petri',
            "diameter":35,
            "orient":"imaged through plate"
            }
    
    
    if 'NGM liquid drop' in row['arena']:
        media = "NGM liquid drop + NGM agar low peptone"
    else:
        media = "NGM agar low peptone"
    
    experiment_info['media'] = media
    experiment_info['food'] = row['food']
    experiment_info['strain'] = row['strain']
    experiment_info['gene'] = row['gene']
    experiment_info['allele'] = row['allele']
    experiment_info['chromosome'] = row['chromosome']
    experiment_info['genotype'] = row['genotype']
    
    
    experiment_info['sex'] = row['sex']
    experiment_info['stage'] = row['developmental_stage']
    if experiment_info['stage'] == "young adult":
        experiment_info['stage'] = 'adult'
    
    experiment_info['ventral_side'] = row['ventral_side']
    
    
    if row['habituation'] == 'NONE':
        hab = "no wait before recording starts."
    else:
        hab = "worm transferred to arena 30 minutes before recording starts."
    experiment_info['protocol'] = [
        "method in E. Yemini et al. doi:10.1038/nmeth.2560",
        hab
    ]
    
    experiment_info['habituation'] = row['habituation']
    experiment_info['tracker'] = row['tracker']
    experiment_info['original_video_name'] = row['original_video']
    
    
    return experiment_info

#%%
def add_exp_info(fname, experiment_info_str):
    with tables.File(fname, 'r+') as fid:
        if '/experiment_info' in fid:
            fid.remove_node('/', 'experiment_info')
        fid.create_array('/', 'experiment_info', obj = experiment_info_str)


def fetch_exp_info(cur, base_name):
    
    cur.execute("SELECT * FROM experiments_full WHERE base_name='{}';".format(base_name))
    row = cur.fetchone()
    experiment_info = db_row2dict(row)
    experiment_info_str = bytes(json.dumps(experiment_info), 'utf-8')
    return experiment_info_str
    


if __name__ == '__main__':
    video_dir_root = '/Volumes/behavgenom_archive$/single_worm/MaskedVideos'
    
    ONLY_UNFINSHED = True
    
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute('USE `single_worm_db`;')
    
    if ONLY_UNFINSHED:
        sql = '''
        SELECT mask_file 
        FROM analysis_progress
        WHERE exit_flag_id <= (SELECT f.id FROM exit_flags as f WHERE checkpoint="CONTOUR_ORIENT")
        AND exit_flag_id > (SELECT f.id FROM exit_flags as f WHERE checkpoint="COMPRESS")
        '''
        cur.execute(sql)
        valid_files = cur.fetchall()
        valid_files = [x['mask_file'] for x in valid_files]
    else:
        valid_files = walkAndFindValidFiles(video_dir_root, pattern_include = '*.hdf5')
    
    
    for ii, mask_file in enumerate(valid_files):
        base_name = os.path.basename(mask_file).replace('.hdf5', '')
        print('{} of {} : {}'.format(ii+1, len(valid_files), base_name))
        
        experiment_info_str = fetch_exp_info(cur, base_name)
        add_exp_info(mask_file, experiment_info_str)
        
        skeletons_file = mask_file.replace('MaskedVideos', 'Results').replace('.hdf5', '_skeletons.hdf5')
        if os.path.exists(skeletons_file):
            add_exp_info(skeletons_file, experiment_info_str)
    
        features_file = mask_file.replace('MaskedVideos', 'Results').replace('.hdf5', '_features.hdf5')
        if os.path.exists(features_file):
            add_exp_info(features_file, experiment_info_str)
            