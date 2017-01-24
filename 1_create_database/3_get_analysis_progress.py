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
from MWTracker.processing.AnalysisPoints import AnalysisPoints
from MWTracker.processing.batchProcHelperFunc import getDefaultSequence
from MWTracker.analysis.feat_create.obtainFeatures import getFPS

import MWTracker
params_dir = os.path.join(os.path.dirname(MWTracker.__file__), 'misc', 'param_files')



def get_progress_data(experiment_id, exit_flag_id, ap_obj):
    out = {}
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
            skel = fid.get_node('/skeletons')[:,0,0] #use it as a proxy of valid skeletons
            if skel.size > 0:
                out['n_valid_skeletons'] = int(np.sum(~np.isnan(skel)))
                out['n_timestamps'] = len(skel)
            else:
                out['n_valid_skeletons'] = 0
                out['n_timestamps'] = 0
    return out

def update_row(cur, experiment_id, 
              exit_flag_id, 
              mask_file=None, 
              skeletons_file=None, 
              features_file=None,
              n_valid_frames=None, 
              n_missing_frames=None,
              n_segmented_skeletons=None, 
              n_filtered_skeletons=None,
              n_valid_skeletons=None, 
              n_timestamps=None,
              first_skel_frame=None, 
              last_skel_frame=None,
              fps=None,
              total_time=None):
    
    dat = [experiment_id, exit_flag_id, 
    mask_file, skeletons_file, features_file, n_valid_frames, 
    n_missing_frames, n_segmented_skeletons, n_filtered_skeletons, 
    n_valid_skeletons, n_timestamps, first_skel_frame, last_skel_frame, 
    fps, total_time]
    
    dat = [x if x is not None else 'NULL' for x in dat]
    
    sql = '''
    INSERT INTO `progress_analysis` (experiment_id, exit_flag_id, 
    mask_file, skeletons_file, features_file, n_valid_frames, 
    n_missing_frames, n_segmented_skeletons, n_filtered_skeletons, 
    n_valid_skeletons, n_timestamps, first_skel_frame, last_skel_frame, 
    fps, total_time) 
    VALUES ({}, {}, "{}", "{}", "{}", {}, {}, {}, {}, {}, {}, {}, {}, {}, {})    
    ON DUPLICATE KEY UPDATE 
    experiment_id=experiment_id, 
    exit_flag_id=exit_flag_id,
    mask_file=mask_file,
    skeletons_file=skeletons_file, 
    features_file=features_file,
    n_valid_frames=n_valid_frames, 
    n_missing_frames=n_missing_frames,
    n_segmented_skeletons=n_segmented_skeletons,
    n_filtered_skeletons=n_filtered_skeletons, 
    n_valid_skeletons=n_valid_skeletons,
    n_timestamps=n_timestamps,
    first_skel_frame=first_skel_frame,
    last_skel_frame=last_skel_frame, 
    fps=fps, 
    total_time=total_time
    '''.format(*dat)
    
    cur.execute(sql)
    
    pass

def get_last_finished(ap_obj, cur, all_points):
    unfinished = ap_obj.getUnfinishedPoints(all_points)
    last_point = 'UNPROCESSED'
    for point in all_points:
        if not point in unfinished:
            last_point = point
            
    cur.execute("SELECT id FROM exit_flags WHERE checkpoint='{}'".format(last_point))
    exit_flag_id = cur.fetchone()        
    exit_flag_id = exit_flag_id['id']
    
    return exit_flag_id, last_point

if __name__ == '__main__':
    
    json_file = os.path.join(params_dir, 'single_worm_on_food.json')
    
    all_points = getDefaultSequence('All', is_single_worm=True)
    
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    cur.execute('USE `single_worm_db`;')
    cur.execute("SELECT id, original_video, base_name FROM experiments_full;")
    all_rows = cur.fetchall()
    
    
    
    for row in all_rows:
        main_file = os.path.realpath(row['original_video'])
        video_dir = os.path.dirname(main_file)
        masks_dir = video_dir.replace('thecus', 'MaskedVideos')
        results_dir = video_dir.replace('thecus', 'Results')
    
        ap_obj = AnalysisPoints(main_file, masks_dir, results_dir, json_file)
        exit_flag_id, last_point = get_last_finished(ap_obj, cur, all_points)
        
        out = get_progress_data(row['id'],  exit_flag_id, ap_obj)
        update_row(cur, **out)
        
        print(row['id'], last_point)
    
    cur.close()
    conn.close()
