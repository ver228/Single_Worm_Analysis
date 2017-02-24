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
from tierpsy.analysis.compress.selectVideoReader import selectVideoReader

from tierpsy.analysis.stage_aligment.alignStageMotion import alignStageMotion, isGoodStageAligment

def get_diff_from_video(original_video):
    frame_diffs = []
    prev_img = None
    vid = selectVideoReader(original_video)
    frame = 0
    ret = 0
    while 1:
        ret, image = vid.read()
        if ret == 0:
            break
        
        frame += 1
        image = image.astype(np.double)
        if prev_img is not None:
            dd = np.var(image-prev_img)
            frame_diffs.append(dd)
            
        prev_img = image
        
        print(frame)
    
    return np.array(frame_diffs)


if __name__ == '__main__':
    test_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3'
    
    original_video = '/Volumes/behavgenom_archive$/single_worm/orignal_videos/single_worm_raw_bkp10/thecus/nas207-3/Data/from pc207-16/Laura/26-02-10/N2 on food L_2010_02_26__08_44_59___7___1.avi'
    results_dir = '/Volumes/behavgenom_archive$/single_worm/unfinished/WT/N2/food_OP50/XX/30m_wait/clockwise'
    base_name = 'N2 on food L_2010_02_26__08_44_59___7___1'
    
    
#    original_video = '/Volumes/behavgenom_archive$/single_worm/orignal_videos/single_worm_raw_bkp10/thecus/nas207-3/Data/from pc207-16/Laura/28-01-10/tbh-1 (n3247)X on food L_2010_01_28__12_38_46___7___7.avi'
#    results_dir = '/Volumes/behavgenom_archive$/single_worm/unfinished/mutants/tbh-1(n3247)X@MT9455/food_OP50/XX/30m_wait/clockwise'
#    base_name = 'tbh-1 (n3247)X on food L_2010_01_28__12_38_46___7___7'
#    
    mask_test = os.path.join(test_dir, base_name + '.hdf5')
    skel_test = os.path.join(test_dir, base_name + '_skeletons.hdf5')
    
        
    frame_diffs_vid = get_diff_from_video(original_video)
    #%%
    with tables.File(skel_test, 'r+') as fid:
        stage_vec = fid.remove_node('/stage_movement/frame_diffs')
        fid.create_array('/stage_movement', 'frame_diffs', obj=frame_diffs_vid ,createparents=True)

    #%%
    
    alignStageMotion(mask_test, skel_test)
    #%%
    skel_file = os.path.join(results_dir, base_name + '_skeletons.hdf5')
    with tables.File(skel_file) as fid:
        flag = fid.get_node('/stage_movement')._v_attrs['has_finished']
        stage_vec = fid.get_node('/stage_movement/stage_vec')[:]
        frame_diffs_mask = fid.get_node('/stage_movement/frame_diffs')[:]
        print(flag)

    with tables.File(skel_test) as fid:
        flag_test = fid.get_node('/stage_movement')._v_attrs['has_finished']
        stage_vec_test = fid.get_node('/stage_movement/stage_vec')[:]
        frame_diffs_vid = fid.get_node('/stage_movement/frame_diffs')[:]
        print(flag_test)
    #%%
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(stage_vec[:,1], 'x')
    plt.plot(stage_vec_test[:,1], '.r')
    plt.subplot(2,1,2)
    plt.plot(stage_vec[:,0], 'x')
    plt.plot(stage_vec_test[:,0], '.r')
    
    #%%
    
    plt.figure()
    plt.plot(frame_diffs_vid, frame_diffs_mask,'.')
    #%%
    plt.figure()
    plt.plot(frame_diffs_mask/np.max(frame_diffs_mask))
    plt.plot(frame_diffs_vid/np.max(frame_diffs_vid))
    
    #%%
    #with tables.File(file_skel) as fid:
    #    frame_diffs_mask = fid.get_node('/stage_movement/frame_diffs')[:]
    