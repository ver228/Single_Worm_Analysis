#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 09:13:02 2018

@author: ajaver
"""
from tierpsy.analysis.ske_create.helperIterROI import getWormROI
import pandas as pd
import tables
import os
import matplotlib.pylab as plt

def make_plots(mask_file, tt, w_index, set_type, save_dir = '.'):
    feat_file = mask_file.replace('.hdf5', '_features.hdf5').replace('MaskedVideos', 'Results')
    skel_file = feat_file.replace('_features.hdf5', '_skeletons.hdf5')
    
    with pd.HDFStore(feat_file, 'r') as fid:
        timeseries_data = fid['/features_timeseries']
    
    t_last = min(tt + 500, timeseries_data['timestamp'].max())
    
    with pd.HDFStore(skel_file, 'r') as fid:
        trajectories_data = fid['/trajectories_data']
    
    #the data in timeseries_data is filter by skeleton
    good = trajectories_data['worm_index_joined'].isin(timeseries_data['worm_index'])
    trajectories_data = trajectories_data[good]
    
    traj_g = trajectories_data.groupby('frame_number')
    frame_data = traj_g.get_group(tt)
    
    ts_g = timeseries_data.groupby('timestamp')
    ts_frame_data = ts_g.get_group(tt)
    
    with tables.File(mask_file, 'r') as fid:
        img = fid.get_node('/mask')[tt]
        
        save_full = fid.get_node('/full_data')._v_attrs['save_interval']
        img_full = fid.get_node('/full_data')[tt//save_full]
        
        
    plt.figure(figsize = (10,6))
    if set_type == 'pycelegans':
        plt.subplot(2,1,1)
        plt.imshow(img_full.T, interpolation='none', cmap='gray')
        plt.axis('off')
        
        plt.subplot(2,1,2)
        plt.imshow(img.T, interpolation='none', cmap='gray')
        
        #add all the worms identified
        for _, row in frame_data.iterrows():
            col = 'tomato' if row['worm_index_joined'] == w_index else 'g'
            cc = plt.Circle((row['coord_y'], row['coord_x']), row['roi_size']/2, lw=2, color=col, fill=False)
            plt.gca().add_artist(cc)
        
        plt.axis('off')
    else:
        plt.subplot(1,2,1)
        plt.imshow(img_full, interpolation='none', cmap='gray')
        plt.axis('off')
        
        plt.subplot(1,2,2)
        plt.imshow(img, interpolation='none', cmap='gray')
        
        #add all the worms identified
        for _, row in frame_data.iterrows():
            col = 'tomato' if row['worm_index_joined'] == w_index else 'g'
            cc = plt.Circle((row['coord_x'], row['coord_y']), row['roi_size']/2, lw=2, color=col, fill=False)
            plt.gca().add_artist(cc)
        
        plt.axis('off')
    
    plt.subplots_adjust(wspace=0.02, hspace=0.02)
    plt.savefig(os.path.join(save_dir, set_type + '_img.pdf'), bbox_inches='tight')
    
    ###
    dat = timeseries_data[timeseries_data['worm_index'] == w_index]
    
    feats = ['head_bend_mean', 'length']#'midbody_bend_mean', 'tail_bend_mean']
    feat_d = ['Head Bend\nMean [deg]', 'Length [pix]']
    
    f, axs = plt.subplots(len(feats),1, sharex=True, sharey=False, figsize=(10,3))
    for i_feat, feat in enumerate(feats):
        #plt.subplot(3,1,i_feat+1)
        axs[i_feat].plot(dat['timestamp'], dat[feat])
        
        #axs[i_feat].set_ylabel(feat.split('_')[0].title())
        axs[i_feat].set_ylabel(feat_d[i_feat])
        axs[i_feat].get_yaxis().set_label_coords(-0.06,0.5)
    
    plt.xlabel('Frame Number')
    plt.xlim(tt, t_last)
    
    plt.savefig(os.path.join(save_dir, set_type + '_ts.pdf'), bbox_inches='tight')

    ####
    row = frame_data[frame_data['worm_index_joined'] == w_index].iloc[0]
    worm_img, roi_corner = getWormROI(img, row['coord_x'], row['coord_y'], row['roi_size'])
    
    plt.figure(figsize=(2,2))
    plt.imshow(worm_img, interpolation='none', cmap='gray')
    
    
    r_ind = ts_frame_data[ts_frame_data['worm_index'] == w_index].index[0]
    with tables.File(feat_file, 'r') as fid:
        cc1 = fid.get_node('/coordinates/dorsal_contours')[r_ind] - roi_corner
        cc2 = fid.get_node('/coordinates/ventral_contours')[r_ind] - roi_corner
        ss = fid.get_node('/coordinates/skeletons')[r_ind] - roi_corner
        
    plt.plot(ss[:, 0], ss[:, 1], 'r')
    plt.plot(cc1[:, 0], cc1[:, 1], 'tomato')
    plt.plot(cc2[:, 0], cc2[:, 1], color='salmon')
    plt.plot(ss[0, 0], ss[0, 1], 'or')
    
    plt.axis('off')

    plt.savefig(os.path.join(save_dir, set_type + '_skel.pdf'), bbox_inches='tight')

if __name__ == '__main__':
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/paper_tierpsy_tracker/different_setups/'
    
    DD = [
    dict(set_type = 'CeLeST',
    mask_file = os.path.join(main_dir, 'CeLeST/MaskedVideos/Sample01/Sample01.hdf5'),
    tt = 0,
    w_index = 1),
    
    dict(set_type = '100E',
    mask_file = os.path.join(main_dir, '100_microscope/MaskedVideos/journal.pbio.2002702.s008.hdf5'),
    tt = 3,
    w_index = 10),
    
    dict(set_type = 'maggots',
    mask_file = os.path.join(main_dir, 'maggots/MaskedVideos/maggots_example.hdf5'),
    tt = 0,
    w_index = 1),
    
    dict(set_type = 'pycelegans',
    mask_file = os.path.join(main_dir, 'pycelegans/MaskedVideos/NT00029_cam1_W001_110722_1649_cam1_M00001/NT00029_cam1_W001_110722_1649_cam1_M00001.hdf5'),
    tt = 1000,
    w_index = 1),
    
    dict(set_type = 'swimming',
    mask_file = os.path.join(main_dir, 'swimming/MaskedVideos/celengas_swimming.hdf5'),
    tt = 0,
    w_index = 7),
    ]
    #%%
    for dd in DD:
        make_plots(**dd)
        