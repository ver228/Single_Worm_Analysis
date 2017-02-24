#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 15:14:22 2017

@author: ajaver
"""
import os
import tables
import matplotlib.pylab as plt
import numpy as np
import copy

from tierpsy.analysis.compress.selectVideoReader import selectVideoReader

from tierpsy.analysis.feat_create.obtainFeatures import \
correctSingleWorm, getMicronsPerPixel, WormFromTable, getOpenWormData, WormStatsClass
#%%
def _get_skels(feat_file):
    with tables.File(feat_file, 'r') as fid:
        if '/features_timeseries' in fid and \
        fid.get_node('/features_timeseries').shape[0]>0:
            skeletons = fid.get_node('/coordinates/skeletons')[:]
            frame_range = fid.get_node('/features_events/worm_1')._v_attrs['frame_range']
    
            #length_avg = np.nanmean(fid.get_node('/features_timeseries').col("length"))
        
            #load rotation matrix to compare with the segworm
            #with tables.File(skel_file, 'r') as fid:
            #    rotation_matrix = fid.get_node('/stage_movement')._v_attrs['rotation_matrix']
            
            #pad the beginign with np.nan to have the same reference as segworm (frame 0)
            skeletons = np.pad(skeletons, [(frame_range[0],0), (0,0), (0,0)], 
                           'constant', constant_values = np.nan)
            return skeletons
#%%
if __name__ == '__main__':
    test_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3'
    
    original_video = '/Volumes/behavgenom_archive$/single_worm/orignal_videos/single_worm_raw_bkp10/thecus/nas207-3/Data/from pc207-16/Laura/26-02-10/N2 on food L_2010_02_26__08_44_59___7___1.avi'
    results_dir = '/Volumes/behavgenom_archive$/single_worm/unfinished/WT/N2/food_OP50/XX/30m_wait/clockwise'
    base_name = 'N2 on food L_2010_02_26__08_44_59___7___1'
    
    
#    original_video = '/Volumes/behavgenom_archive$/single_worm/orignal_videos/single_worm_raw_bkp10/thecus/nas207-3/Data/from pc207-16/Laura/28-01-10/tbh-1 (n3247)X on food L_2010_01_28__12_38_46___7___7.avi'
#    results_dir = '/Volumes/behavgenom_archive$/single_worm/unfinished/mutants/tbh-1(n3247)X@MT9455/food_OP50/XX/30m_wait/clockwise'
#    base_name = 'tbh-1 (n3247)X on food L_2010_01_28__12_38_46___7___7'   
    #%%
    #feat_file = os.path.join(test_dir, base_name + '_features.hdf5')
    #skeletons = _get_skels(feat_file)
    #%%
    skel_file = os.path.join(test_dir, base_name + '_skeletons.hdf5')
    with tables.File(skel_file) as fid:
        flag = fid.get_node('/stage_movement')._v_attrs['has_finished']
        stage_vec = fid.get_node('/stage_movement/stage_vec')[:]
        frame_diffs_mask = fid.get_node('/stage_movement/frame_diffs')[:]
    

    #%%
    micronsPerPixel = getMicronsPerPixel(skel_file)
    worm = WormFromTable(
                skel_file,
                1,
                use_skel_filter=True,
                worm_index_str='worm_index_joined',
                micronsPerPixel=micronsPerPixel,
                fps=30,
                smooth_window=-1)
    worm2 = copy.copy(worm)
    
    worm = correctSingleWorm(worm, skel_file)
    wStats = WormStatsClass()
    #timeseries_data, events_data, worm_stats, worm_coords= \
    #            getOpenWormData(worm, wStats)
    #%%
    
#%%
#    for field in ['skeleton', 'ventral_contour', 'dorsal_contour']:
#        if hasattr(worm, field):
#            tmp_dat = getattr(worm, field)
#            # rotate the skeletons
#            # for ii in range(tot_skel):
#        #tmp_dat[ii] = np.dot(rotation_matrix, tmp_dat[ii].T).T
#            tmp_dat = tmp_dat + stage_vec_inv[:, np.newaxis, :]
#            setattr(worm, field, tmp_dat)