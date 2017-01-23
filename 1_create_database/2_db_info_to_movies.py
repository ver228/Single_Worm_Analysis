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

from MWTracker.processing.batchProcHelperFunc import walkAndFindValidFiles

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
    experiment_info['arena'] = row['arena']
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
    
    experiment_info['tracker'] = row['tracker']
    experiment_info['original_video_name'] = row['original_video_name']
    experiment_info['habituation'] = row['habituation']
    
    return experiment_info

#%%
if __name__ == '__main__':
    video_dir_root = '/Volumes/behavgenom_archive$/single_worm/MaskedVideos'
    valid_files = walkAndFindValidFiles(video_dir_root, pattern_include = '*.hdf5')
    
    
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    for ii, fname in enumerate(valid_files):
        base_name = os.path.basename(fname).replace('.hdf5', '')
        
        cur.execute('USE `single_worm_db`;')
        cur.execute("SELECT * FROM experiments_full WHERE base_name='{}';".format(base_name))
        row = cur.fetchone()
        print(row)
        experiment_info = db_row2dict(row)
        experiment_info_str = bytes(json.dumps(experiment_info), 'utf-8')
    
        with tables.File(fname, 'r+') as fid:
            if '/experiment_info' in fid:
                fid.remove_node('/', 'experiment_info')
            fid.create_array('/', 'experiment_info', obj = experiment_info_str)
    
        print('{} of {} : {}'.format(ii+1, len(valid_files), base_name))
        
