# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:17:35 2016

@author: ajaver
"""

import os
import tables
import pandas as pd
import numpy as np
import pymysql.cursors
from collections import OrderedDict
from tierpsy.processing.AnalysisPoints import AnalysisPoints
from tierpsy.processing.batchProcHelperFunc import getDefaultSequence
from tierpsy.analysis.feat_create.obtainFeatures import getFPS
from tierpsy.analysis.stage_aligment.alignStageMotion import isGoodStageAligment

import tierpsy
params_dir = os.path.join(os.path.dirname(tierpsy.__file__), 'misc', 'param_files')
ON_FOOD_JSON = os.path.join(params_dir, 'single_worm_on_food.json')


ALL_POINTS = getDefaultSequence('All', is_single_worm=True)
PROGRESS_TAB_FIELD = ['experiment_id', 'exit_flag_id', 'mask_file', 
    'skeletons_file', 'features_file', 'n_valid_frames', 'n_missing_frames', 
    'n_segmented_skeletons', 'n_filtered_skeletons', 'n_valid_skeletons', 
    'n_timestamps', 'first_skel_frame', 'last_skel_frame', 'fps', 'total_time']

def get_progress_data(experiment_id, exit_flag_id, ap_obj):
    #%%
    out = OrderedDict()
    for x in PROGRESS_TAB_FIELD:
        out[x] = None
    out['experiment_id'] = experiment_id
    out['exit_flag_id'] =exit_flag_id
    
    masked_image_file = ap_obj.file_names['masked_image']
    if os.path.exists(masked_image_file):
        out['mask_file'] = masked_image_file
        with tables.File(masked_image_file, 'r') as fid:
            out['n_valid_frames'] = int(fid.get_node('/mask').shape[0])
        
        fps, _ = getFPS(masked_image_file, None)
        if not fps is None:
            with tables.File(masked_image_file, 'r') as fid:
                timestamp_time = fid.get_node('/timestamp/time')[:]
                timestamp_ind = fid.get_node('/timestamp/raw')[:]
                #sometimes only the last frame is nan
                timestamp_ind = timestamp_ind[~np.isnan(timestamp_time)]
                timestamp_time = timestamp_time[~np.isnan(timestamp_time)]
                assert timestamp_ind.size == timestamp_time.size
                
                out['n_missing_frames'] = int(timestamp_ind[-1] - out['n_valid_frames'] + 1)
                out['total_time'] = float(timestamp_time[-1])
                out['fps'] = float(fps)
        
                
    
    skeletons_file = ap_obj.file_names['skeletons']
    if os.path.exists(skeletons_file):
        out['skeletons_file'] = skeletons_file
    
        with pd.HDFStore(skeletons_file, 'r') as fid:
            trajectories_data = fid['/trajectories_data']
            if len(trajectories_data) > 0:
                out['n_segmented_skeletons'] = int(trajectories_data['has_skeleton'].sum())
                out['first_skel_frame'] = int(trajectories_data['frame_number'].min())
                out['last_skel_frame'] = int(trajectories_data['frame_number'].max())
                if 'is_good_skel' in trajectories_data:
                    out['n_filtered_skeletons'] = int(trajectories_data['is_good_skel'].sum())
    
    features_file = ap_obj.file_names['features']
    if os.path.exists(features_file):
        out['features_file'] = features_file
        with tables.File(features_file, 'r') as fid:
            if '/skeletons' in fid:
                skel = fid.get_node('/skeletons')[:,0,0] #use it as a proxy of valid skeletons
                if skel.size > 0:
                    out['n_valid_skeletons'] = int(np.sum(~np.isnan(skel)))
                    out['n_timestamps'] = len(skel)
                else:
                    out['n_valid_skeletons'] = 0
                    out['n_timestamps'] = 0
    return out

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
    INSERT INTO `analysis_progress` ({}) 
    VALUES ({})    
    ON DUPLICATE KEY UPDATE {}
    '''.format(names_str, values_str, update_str)
    
    cur.execute(sql)
    
    

def get_last_finished(ap_obj, cur):
    #%%
    def _get_flag_name(_ap_obj):
        unfinished = _ap_obj.getUnfinishedPoints(ALL_POINTS)
    
        if not unfinished:
            return 'END'
        else:
            if not 'STAGE_ALIGMENT' in unfinished:
                if not isGoodStageAligment(_ap_obj.file_names['skeletons']):
                    return 'FAIL_STAGE_ALIGMENT'
            
            for point in ALL_POINTS:
                if point in unfinished:
                    return point
#%%    
    last_point = _get_flag_name(ap_obj)
    
    cur.execute("SELECT id FROM exit_flags WHERE checkpoint='{}'".format(last_point))
    exit_flag_id = cur.fetchone()
        
    exit_flag_id = exit_flag_id['id']
    
    return exit_flag_id, last_point

if __name__ == '__main__':
    CHECK_ONLY_UNFINISHED = True
    
    
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    cur.execute('USE `single_worm_db`;')
    
    sql = "SELECT id, original_video, base_name FROM experiments_full"
 
    
    if CHECK_ONLY_UNFINISHED:
        last_valid = 'STAGE_ALIGMENT'
        
        sql_fin_ind = '''
        SELECT experiment_id 
        FROM analysis_progress 
        WHERE exit_flag_id >= (SELECT f.id FROM exit_flags as f WHERE checkpoint="{}")
        
        '''.format(last_valid)
        #AND exit_flag_id < 100
        
        sql += '''
        WHERE id NOT IN 
        ({}) 
        '''.format(sql_fin_ind)                     
    cur.execute(sql)
    all_rows = cur.fetchall()
    
    print('*******', len(all_rows))
    for irow, row in enumerate(all_rows):
        main_file = os.path.realpath(row['original_video'])
        video_dir = os.path.dirname(main_file)
        masks_dir = video_dir.replace('thecus', 'MaskedVideos')
        results_dir = video_dir.replace('thecus', 'Results')
        ap_obj = AnalysisPoints(main_file, masks_dir, results_dir, ON_FOOD_JSON)
        
        exit_flag_id, last_point = get_last_finished(ap_obj, cur)
        
        row_input = get_progress_data(row['id'],  exit_flag_id, ap_obj)
        update_row(cur, row_input)
        
        print(row['id'], last_point)
        conn.commit()    
            
    conn.commit()
    cur.close()
    conn.close()
