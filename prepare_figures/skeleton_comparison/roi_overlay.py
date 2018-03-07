#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 14:15:22 2017

@author: ajaver
"""
import numpy as np
import matplotlib.pylab as plt

import sys
sys.path.append('../../compare_segworm')
from read_feats import FeatsReaderComp

def _get_length(skels):
    dxy2 = np.diff(skels, axis=1)**2
    dr = np.sqrt(np.sum(dxy2, axis=2))
    ll = np.sum(dr, axis=1)
    return ll


def _get_error(skeletons, skel_segworm):
    max_n_skel = min(skel_segworm.shape[0], skeletons.shape[0])
    delS = skeletons[:max_n_skel]-skel_segworm[:max_n_skel]
    R_error = delS[:,:,0]**2 + delS[:,:,1]**2
    skel_error = np.sqrt(np.mean(R_error, axis=1))
    return skel_error

if __name__ == '__main__':
    #%%
    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/WT/AQ2947/food_OP50/XX/30m_wait/anticlockwise/483 AQ2947 on food R_2012_03_08__15_42_48___1___8.hdf5
/Volumes/behavgenom$/Andre/Laura Grundy/gene_NA/allele_NA/AQ2947/on_food/XX/30m_wait/L/tracker_1/2012-03-08___15_42_48/483 AQ2947 on food R_2012_03_08__15_42_48___1___8_features.mat'''
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/WT/AQ2947/food_OP50/XX/30m_wait/anticlockwise/483 AQ2947 on food R_2012_03_08__15_42_48___1___8.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/gene_NA/allele_NA/AQ2947/on_food/XX/30m_wait/L/tracker_1/2012-03-08___15_42_48/483 AQ2947 on food R_2012_03_08__15_42_48___1___8_features.mat'''

    feat_file, segworm_feat_file = dd.split('\n')
    feat_file = feat_file.replace('.hdf5', '_features.hdf5')
    
    feats_reader = FeatsReaderComp(feat_file, segworm_feat_file)
    skeletons, skel_segworm = feats_reader.read_skeletons()
    
    skel_error = _get_error(skeletons, skel_segworm)
    skel_error_switch = _get_error(skeletons[:, ::-1], skel_segworm)
    
    skel_error = np.where(skel_error_switch<skel_error, skel_error_switch, skel_error)
    
    max_n_skel = min(skel_segworm.shape[0], skeletons.shape[0])
    L = _get_length(skeletons[:max_n_skel])
    skel_error = skel_error/L
    
    
    
    
    import tables
    mask_file = feat_file.replace('_features.hdf5', '.hdf5')
    
    
    #%%
    ind_t, = np.where(skel_error>0.02)
    tt = 7166#ind_t[2]
    #tt = np.nanargmax(skel_error)
    #tt = 938
    with tables.File(mask_file, 'r') as fid:
        img = fid.get_node('/mask')[tt]
        microns_per_pixel = fid.get_node('/mask')._v_attrs['microns_per_pixel']
    
    skeletons_c = (skeletons[:max_n_skel] - feats_reader.stage_movement[:max_n_skel, None, :])/microns_per_pixel
    skel_segworm_c = (skel_segworm[:max_n_skel] - feats_reader.stage_movement[:max_n_skel, None, :])/microns_per_pixel
    
    plt.figure(figsize=(2,2))
    plt.imshow(img, cmap='gray', interpolation='None')
    
    plt.plot(skeletons_c[tt, :, 0].T, skeletons_c[tt, :, 1].T, 'x', color='mediumaquamarine', markersize=2)
    plt.plot(skeletons_c[tt, 0, 0].T, skeletons_c[tt, 0, 1].T, '^', color='mediumaquamarine', markersize=4)
    plt.plot(skel_segworm_c[tt, :, 0].T, skel_segworm_c[tt, :, 1].T, 'o', color='tomato', markersize=1)
    plt.plot(skel_segworm_c[tt, 0, 0].T, skel_segworm_c[tt, 0, 1].T, 'v', color='tomato', markersize=3)
    
    plt.xlim((250, 410))
    plt.ylim((190, 360))
    #plt.xlim((150, 450))
    #plt.ylim((140, 280))
    
    plt.xticks([])
    plt.yticks([])
    
    scale_v = 150
    scale_l = scale_v/microns_per_pixel
    plt.text(253, 200, '{}$\mu$m'.format(scale_v), fontsize=10, color='w')
    plt.plot((255, 255 + scale_l), (195, 195), lw=2, color='w')
    
    
    plt.text(309, 345, 'RMSE/L:{:.3f}'.format(skel_error[tt]), fontsize=10, color='w')
    
    plt.tight_layout()
    plt.savefig('ROI_RMSE.pdf')
    