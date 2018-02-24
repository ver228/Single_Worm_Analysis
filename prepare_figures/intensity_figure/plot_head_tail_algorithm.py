#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 22:25:15 2018

@author: ajaver
"""
import tables
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import matplotlib.patches as patches
from scipy.ndimage.filters import median_filter,  minimum_filter, maximum_filter

def getDampFactor(length_resampling):
    # this is small window that reduce the values on the head a tail, where a
    # segmentation error or noise can have a very big effect
    MM = length_resampling // 4
    rr = (np.arange(MM) / (MM - 1)) * 0.9 + 0.1
    damp_factor = np.ones(length_resampling)
    damp_factor[:MM] = rr
    damp_factor[-MM:] = rr[::-1]
    return damp_factor

def correctHeadTailIntWorm(
        trajectories_worm,
        skeletons_file,
        intensities_file,
        smooth_W=5,
        gap_size=0,
        min_block_size=10,
        local_avg_win=25,
        min_frac_in=0.85,
        method='MEDIAN_INT'):

    # get data with valid intensity maps (worm int profile)
    good = trajectories_worm['int_map_id'] != -1
    int_map_id = trajectories_worm.loc[good, 'int_map_id'].values
    
    # only analyze data that contains at least  min_block_size intensity
    # profiles
    if int_map_id.size == 0 or int_map_id.size < min_block_size:
        return []

    # read the worm intensity profiles
    with tables.File(intensities_file, 'r') as fid:
        worm_int_profile = fid.get_node(
            '/straighten_worm_intensity_median')[int_map_id, :]

    # normalize intensities of each individual profile
    worm_int_profile -= np.median(worm_int_profile, axis=1)[:, np.newaxis]

    # reduce the importance of the head and tail. This parts are typically
    # more noisy
    damp_factor = getDampFactor(worm_int_profile.shape[1])
    worm_int_profile *= damp_factor
    if method == 'HEAD_BRIGHTER':
        segmentIndex = worm_int_profile.shape[1]//5
        top_part = worm_int_profile[:,1:segmentIndex].astype(np.float)
        bot_part = worm_int_profile[:,-segmentIndex:].astype(np.float)
        # get the difference between the max of the first part and the min of the last part of skeleton
        #diff_ori = np.abs(np.median(top_part, axis=1) - np.min(bot_part, axis=1)) # diff_inv should be high when the orientation is correct
        #diff_inv = np.abs(np.min(top_part, axis=1) - np.max(bot_part, axis=1)) # diff_ori should be high when the orientation is incorrect
        diff_inv = np.median(top_part, axis=1) - np.median(bot_part, axis=1) #diff_inv should be high when the orientation is correct
        diff_ori = 0

    else: # default method is 'MEDIAN_INT'
        # worm median intensity
        med_int = np.median(worm_int_profile, axis=0).astype(np.float)

        # let's check for head tail errors by comparing the
        # total absolute difference between profiles using the original
        # orientation ...
        diff_ori = np.mean(np.abs(med_int - worm_int_profile), axis=1)
        #... and inverting the orientation
        diff_inv = np.mean(np.abs(med_int[::-1] - worm_int_profile), axis=1)

    
    # smooth data, it is easier for identification
    diff_ori_med = median_filter(diff_ori, smooth_W)
    diff_inv_med = median_filter(diff_inv, smooth_W)

    # this will increase the distance between the original and the inversion.
    # Therefore it will become more stringent on detection
    diff_orim = minimum_filter(diff_ori_med, smooth_W)
    diff_invM = maximum_filter(diff_inv_med, smooth_W)
    
    # a segment with a bad head-tail indentification should have a lower
    # difference with the median when the profile is inverted.
    bad_orientationM = diff_orim > diff_invM


    return worm_int_profile, diff_ori_med,  diff_inv_med, bad_orientationM

#%%
if __name__ == '__main__':
    #mask_file = '/Users/ajaver/OneDrive - Imperial College London/paper_tierpsy_tracker/figures/head_tail_orientation_int/data/N2_worms10_food1-10_Set3_Pos4_Ch3_02062017_123419.hdf5'
    
    mask_file = '/Users/ajaver/OneDrive - Imperial College London/paper_tierpsy_tracker/figures/head_tail_orientation_int/single_worm/L4_H_15_2016_10_30__15_31_01__.hdf5'
    int_file = mask_file.replace('.hdf5', '_intensities.hdf5')
    skel_file = mask_file.replace('.hdf5', '_skeletons.hdf5')
    
    with pd.HDFStore(int_file, 'r') as fid:
        trajectories_data = fid['/trajectories_data_valid']
        
    traj_g = trajectories_data.groupby('worm_index_joined')
    
    for w_ind, trajectories_worm in traj_g:
        #if w_ind != 417: continue
        
        worm_int_profile, diff_ori_med,  diff_inv_med, bad_orientationM = \
        correctHeadTailIntWorm(trajectories_worm, skel_file, int_file)
        
        
        
        if bad_orientationM.sum() > 0:
            #%%
            profile_ts = (5050, 5300, 5950)
            profile_cc = ('orange', 'orangered',  'salmon')
            wrong_ts = (5240, 5357)
            
            y_lim_d = (0, 131)
            x_lim_d = (5000, 6000)
            
            print(w_ind, bad_orientationM.sum(), worm_int_profile.shape[0])
            plt.figure(figsize=(12, 12))
            
            plt.subplot(3,1,2)
            plt.imshow(worm_int_profile.astype(np.float32).T, 
                       aspect = 'auto', 
                       interpolation='none', 
                       cmap='gray')
            plt.xlim(*x_lim_d)
            plt.ylim(*y_lim_d)
            
            
            for rr, cc in zip(profile_ts, profile_cc):
                plt.plot((rr,rr), y_lim_d, '-', color=cc, lw=4)
            
            plt.yticks([])
            plt.xticks([])
            
            plt.ylabel('Tail $\Longrightarrow$ Head', fontsize=20)
            
            plt.ylim(y_lim_d)
            
            
            ax_ = plt.subplot(3,1,3)
            
            y_lim_s3 = (3, 17)
            #for ll in wrong_ts:
            #    plt.plot((ll,ll), y_lim_s3, '--', color='sandybrown', lw=4)
            
            p = patches.Rectangle( (wrong_ts[0], y_lim_s3[0]), 
                                  wrong_ts[1]-wrong_ts[0], 
                                  y_lim_s3[1] - y_lim_s3[0],
                                  alpha=0.1, 
                                  color = 'r')
            ax_.add_patch(p)
            
            plt.plot(diff_ori_med, label='Original', lw=3)
            plt.plot(diff_inv_med, label='Inverted', lw=3)
            plt.xlim(*x_lim_d)
            plt.ylim(*y_lim_s3)
            
            plt.xlabel('Frame Number', fontsize = 18)
            plt.ylabel(r'$\frac{1}{n}\sum{|I - I_{mean}|}$', fontsize = 22)
            plt.legend(fontsize=18)
            plt.tight_layout()
            
            plt.tick_params(axis='both', which='major', labelsize=14)
            
            straighten_worm = np.median(worm_int_profile, axis=0)
            
            axs = []
            
            for ii, (tt,cc) in enumerate(zip(profile_ts, profile_cc)):
                ax = plt.subplot(3, 3,  ii + 1)
                axs.append(ax)
                plt.plot(worm_int_profile[tt], lw=3, color=cc, label='Frame Intensity')
                plt.plot(straighten_worm, lw=3, color='dodgerblue', label='Median Intensity')
                #plt.axis('off')
                
                plt.yticks([])
                plt.xticks([])
                
                # Hide the right and top spines
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                plt.xlabel('Tail $\Longrightarrow$ Head', fontsize=16)
                plt.ylabel('Intensity', fontsize=16)
                
                plt.ylim(-38, 35)
                tt_s = 'frame: {}'.format(tt)
                ax.text(0.35, .9, tt_s, transform=ax.transAxes,fontsize=14)
                
                
                
            axs[0].set_zorder(1)
            axs[0].legend(fontsize=18,  bbox_to_anchor=(0.35, 0.3))
            
            #plt.subplots_adjust(wspace=None)
            plt.savefig('intensity_ht_correct.pdf')
            
        
        