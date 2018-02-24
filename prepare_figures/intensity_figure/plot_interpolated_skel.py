#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 13:39:29 2018

@author: ajaver
"""
from tierpsy.analysis.int_profile.getIntensityProfile import smoothSkeletons, getStraightenWormInt
from tierpsy.analysis.ske_create.helperIterROI import getWormROI

import pandas as pd
import tables
import matplotlib.pylab as plt

if __name__ == '__main__':
    mask_file = '/Users/ajaver/OneDrive - Imperial College London/paper_tierpsy_tracker/figures/head_tail_orientation_int/data/N2_worms10_food1-10_Set3_Pos4_Ch3_02062017_123419.hdf5'
    int_file = mask_file.replace('.hdf5', '_intensities.hdf5')
    skel_file = mask_file.replace('.hdf5', '_skeletons.hdf5')
    
    with pd.HDFStore(int_file, 'r') as fid:
        trajectories_data = fid['/trajectories_data_valid']
    traj_g = trajectories_data.groupby('worm_index_joined')
    
    trajectory_data = traj_g.get_group(1)
    
    
    frame_number = 5200
    
    with tables.File(mask_file, 'r') as fid:
        img = fid.get_node('/mask')[frame_number]
    
    row_data = trajectory_data[trajectory_data['frame_number'] == frame_number].iloc[0]
    worm_img, roi_corner = getWormROI(
                    img, row_data['coord_x'], row_data['coord_y'], row_data['roi_size'])
    #%%
    skeleton_id = row_data['skeleton_id']
    with tables.File(skel_file, 'r') as fid:
        skeleton = fid.get_node('/skeleton')[skeleton_id, :, :] - roi_corner
        half_width = fid.get_node('/width_midbody')[skeleton_id]/2

    length_resampling = 131
    width_resampling = 15
    skel_smooth = smoothSkeletons(
        skeleton,
        length_resampling = length_resampling,
        smooth_win = 11,
        pol_degree = 3)
    straighten_worm, grid_x, grid_y = getStraightenWormInt(
        worm_img, skel_smooth, half_width=half_width, 
        width_resampling=width_resampling)


    #%%
    plt.figure(figsize=(12, 4))
    plt.subplot(1,3,1)
    plt.imshow(worm_img, cmap='gray', interpolation='none')
    plt.axis('off')
    
    plt.subplot(1,3,2)
    plt.imshow(worm_img, cmap='gray', interpolation='none')
    plt.plot(grid_x, grid_y)
    plt.plot(skeleton[:,0], skeleton[:,1], 'r', lw=3)
    plt.axis('off')
    
    plt.subplot(1,3,3)
    plt.imshow(straighten_worm.T, cmap='gray', interpolation='none')
    
    w_half = width_resampling/2
    plt.plot((w_half, w_half), (0, length_resampling), '--', color='tomato', lw=3)
    plt.axis('off')
    
    plt.savefig('straigten_worm.pdf')
    
    
    