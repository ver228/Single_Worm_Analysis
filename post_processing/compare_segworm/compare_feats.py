#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 18:35:13 2017

@author: ajaver
"""
import os
import glob
import tables
import numpy as np
from scipy.io import loadmat
import matplotlib.pylab as plt

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
        
def _get_skels_segworm(segworm_feat_file):
    #load segworm data
    fvars = loadmat(segworm_feat_file, struct_as_record=False, squeeze_me=True)
    segworm_x = -fvars['worm'].posture.skeleton.x.T
    segworm_y = -fvars['worm'].posture.skeleton.y.T
    segworm = np.stack((segworm_x,segworm_y), axis=2)
    
    return segworm


def plot_skel_diff(skeletons, skel_segworm, skel_error):
    w_xlim = w_ylim = (-10, skel_error.size+10)
    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(skel_error, '.')
    plt.ylim((0, np.nanmax(skel_error)))
    plt.xlim(w_xlim)
    plt.title('')
    plt.ylabel('Error')
    
    plt.subplot(3,1,2)
    plt.plot(skeletons[:,1, 0], 'b')
    plt.plot(skel_segworm[:,1, 0], 'r')
    plt.xlim(w_ylim)
    plt.ylabel('Y coord')
    
    plt.subplot(3,1,3)
    plt.plot(skeletons[:,1, 1], 'b')
    plt.plot(skel_segworm[:,1, 1], 'r')
    plt.xlim(w_xlim)
    plt.ylabel('X coord')
    plt.xlabel('Frame Number')
    
#    plt.figure()
#    delT = 15
#    #plt.subplot(3,1,1)
#    plt.plot(skel_x[::delT].T, skel_y[::delT].T, 'b')    
#    plt.plot(seg_x[::delT].T, seg_y[::delT].T, 'r')
#    plt.axis('equal')
#    plt.title(mask_id)


if __name__ == '__main__':
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    
    f_list = glob.glob(os.path.join(main_dir, '*_features.mat'))
    
    for segworm_feat_file in f_list:
        feat_file = segworm_feat_file.replace('_features.mat', '_features.hdf5')
        skel_file = segworm_feat_file.replace('_features.mat', '_skeletons.hdf5')
        
        skeletons = _get_skels(feat_file)
        skel_segworm = _get_skels_segworm(segworm_feat_file)
        
        if skeletons is None:
            continue
        
        #load rotation matrix to compare with the segworm
        with tables.File(skel_file, 'r') as fid:
            rotation_matrix = fid.get_node('/stage_movement')._v_attrs['rotation_matrix']
        
        
            microns_per_pixel_scale = fid.get_node(
                    '/stage_movement')._v_attrs['microns_per_pixel_scale']
        
        #correct in case the data has different size shape
        max_n_skel = min(skel_segworm.shape[0], skeletons.shape[0])
        skeletons = skeletons[:max_n_skel]
        skel_segworm = skel_segworm[:max_n_skel]
        
        # rotate skeleton to compensate for camera movement
        dd = np.sign(microns_per_pixel_scale)
        rotation_matrix_inv = np.dot(
            rotation_matrix * [(1, -1), (-1, 1)], [(dd[0], 0), (0, dd[1])])
        for tt in range(skel_segworm.shape[0]):
            skel_segworm[tt] = np.dot(rotation_matrix_inv, skel_segworm[tt].T).T
        
        #shift the skeletons coordinate system to one that diminushes the errors the most.
        seg_shift = np.nanmedian(skeletons-skel_segworm, axis = (0,1))
        skel_segworm += seg_shift
        print(seg_shift)
        #%%
        delS = skeletons-skel_segworm
        R_error = delS[:,:,0]**2 + delS[:,:,1]**2
        skel_error = np.sqrt(np.mean(R_error, axis=1))
        
        plot_skel_diff(skeletons, skel_segworm, skel_error)
#        plt.figure()
#        for tt in range(0, 10000, 1000):
#            xx = skeletons[tt, 25, 0]
#            yy = skeletons[tt, :, 1]
#            plt.plot(xx, yy, '.-b')
#            xx = skel_segworm[tt, :, 0]
#            yy = skel_segworm[tt, :, 1]
#            plt.plot(xx, yy, '.-r')


