#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 16:59:45 2017

@author: ajaver
"""
import os
import json
import tables
import numpy as np
import pymysql.cursors
from collections import OrderedDict

from tierpsy.helper.params import copy_unit_conversions, read_microns_per_pixel
from tierpsy.analysis.stage_aligment.alignStageMotion import isGoodStageAligment, _h_get_stage_inv

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
    experiment_info['strain_description'] = row['strain_description']
    
    
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


def get_exp_info_str(cur, base_name):
    cur.execute("SELECT * FROM experiments_full WHERE base_name='{}';".format(base_name))
    row = cur.fetchone()
    experiment_info = db_row2dict(row)
    experiment_info_str = bytes(json.dumps(experiment_info), 'utf-8')
    return experiment_info_str


def add_extra_info(cur, base_name, results_dir):
    
    valid_fields = ['/mask', '/trajectories_data', '/features_timeseries']
    mask_file = os.path.join(results_dir, base_name + '.hdf5')
    skeletons_file = os.path.join(results_dir, base_name + '_skeletons.hdf5')
    features_file = os.path.join(results_dir, base_name + '_features.hdf5')
    
    def _add_exp_data(fname, experiment_info_str):
        with tables.File(fname, 'r+') as fid:
            if os.path.exists(skeletons_file):
                group_to_save = fid.get_node(field)
                copy_unit_conversions(group_to_save, skeletons_file)
            
            if '/experiment_info' in fid:
                fid.remove_node('/', 'experiment_info')
            fid.create_array('/', 'experiment_info', obj = experiment_info_str)
    
    
    experiment_info_str = get_exp_info_str(cur, base_name)
    
    fnames = [mask_file, skeletons_file, features_file]
    for fname, field in zip(fnames, valid_fields):
        if os.path.exists(fname):
            _add_exp_data(fname, experiment_info_str)
    
    #finally if the stage was aligned correctly add the information into the mask file    
    if os.path.exists(mask_file) and isGoodStageAligment(skeletons_file):
        microns_per_pixel = read_microns_per_pixel(mask_file)
        with tables.File(mask_file, 'r+') as fid:
            n_frames = fid.get_node('/mask').shape[0]
            stage_vec_inv = _h_get_stage_inv(skeletons_file, np.arange(n_frames))
            stage_vec_pix = stage_vec_inv/microns_per_pixel
            if '/stage_position_pix' in fid: 
                fid.remove_node('/', 'stage_position_pix')
            fid.create_array('/', 'stage_position_pix', obj=stage_vec_pix)
            
        
    

    

if __name__ == '__main__':
    video_dir_root = '/Volumes/behavgenom_archive$/single_worm/MaskedVideos'
    
    ONLY_UNFINSHED = True
    
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute('USE `single_worm_db`;')
    
    sql = '''
    SELECT base_name, results_dir
    FROM experiments
    WHERE exit_flag_id > (SELECT f.id FROM exit_flags as f WHERE name="COMPRESS")
    '''
    cur.execute(sql)
    valid_files = cur.fetchall()
    
    
    for ii, row in enumerate(valid_files):
        print('{} of {} : {}'.format(ii+1, len(valid_files), row['base_name']))
        add_extra_info(cur, **row)
        
