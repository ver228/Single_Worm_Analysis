# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 22:01:59 2016

@author: ajaver
"""

import h5py
import tables
import os
import numpy as np
import matplotlib.pylab as plt
from scipy.io import loadmat
import glob
import os
import pandas as pd

main_dir = '/Users/ajaver/Desktop/Videos/single_worm/global_sample_v2/'
#main_dir = '/Users/ajaver/Desktop/Videos/single_worm/global_sample_test2/'
#main_dir = '/Users/ajaver/Desktop/Videos/single_worm/global_sample/'
#main_dir = '/Users/ajaver/Desktop/Videos/single_worm/switched_sample/'
#main_dir = '/Users/ajaver/Desktop/Videos/single_worm/large_errors/'

from MWTracker.featuresAnalysis.obtainFeaturesHelper import WormFromTable
from MWTracker.featuresAnalysis.obtainFeatures import getMicronsPerPixel, getFPS
#%%
files = glob.glob(os.path.join(main_dir, '*.hdf5' ))
files = [x for x in files if not x.endswith('_skeletons.hdf5') \
and not x.endswith('_features.hdf5')]
files = sorted(files)
#files = files[9:10]
#%%
for mask_id in range(len(files)):
    masked_image_file = files[mask_id]
    
    #segworm_feat_file = masked_image_file[:-5] + '_features.mat'
    #dd = os.path.split(masked_image_file[:-5])
    #skeletons_file = os.path.join(dd[0], 'Results', dd[1] + '_skeletons.hdf5')
    #feat_file = os.path.join(dd[0], 'Results', dd[1] + '_features.hdf5')
    
    dd = masked_image_file[:-5]
    dd1 = os.path.split(masked_image_file)
    dd1 = os.path.join(dd1[0], 'Results', dd1[1][:-5])
    skeletons_file = dd1 + '_skeletons.hdf5'
    feat_file = dd1 + '_features.hdf5'
    segworm_feat_file = dd + '_features.mat'
    
    #skeletons_file = masked_image_file.replace('MaskedVideos', 'Results')[:-5] + '_skeletons.hdf5'
    #feat_file = masked_image_file.replace('MaskedVideos', 'Results')[:-5] + '_features.hdf5'
    #segworm_feat_file = masked_image_file.replace('MaskedVideos', 'Features')[:-5] + '_features.mat'

#%%
    print(mask_id, masked_image_file)
    #if not (os.path.exists(skeletons_file) or os.path.exists(feat_file)):
    #    continue
    #%%
    
    with tables.File(skeletons_file, 'r') as fid:
        microns_per_pixel_scale = fid.get_node('/stage_movement')._v_attrs['microns_per_pixel_scale']
        #stage_vec_ori = fid.get_node('/stage_movement/stage_vec')[:]
        timestamp_ind = fid.get_node('/timestamp/raw')[:].astype(np.int)
        rotation_matrix = fid.get_node('/stage_movement')._v_attrs['rotation_matrix']
        skeletons_pix = fid.get_node('/skeleton')[:]
    
    #%%
    skeletons = np.zeros(0) #just to be sure i am not using a skeleton for another file
    try:
        with tables.File(feat_file, 'r') as fid:
            if '/features_means' in fid and \
            fid.get_node('/features_means').attrs['has_finished'] and \
            fid.get_node('/features_timeseries').shape[0]>0:
                skeletons = fid.get_node('/skeletons')[:]
                frame_range = fid.get_node('/features_events/worm_1')._v_attrs['frame_range']
            
                #pad the beginign with np.nan to have the same reference as segworm
                skeletons = np.pad(skeletons, [(frame_range[0],0), (0,0), (0,0)], 
                           'constant', constant_values=np.nan)
            else:
                raise OSError
    except (OSError):
        continue
    
    if os.path.exists(segworm_feat_file):
        fvars = loadmat(segworm_feat_file, struct_as_record=False, squeeze_me=True)
        micronsPerPixels_x = fvars['info'].video.resolution.micronsPerPixels.x
        micronsPerPixels_y = fvars['info'].video.resolution.micronsPerPixels.y
        
        segworm_x = -fvars['worm'].posture.skeleton.x.T
        segworm_y = -fvars['worm'].posture.skeleton.y.T
        
        
        segworm = np.stack((segworm_x,segworm_y), axis=2)
        #rotation_matrix_inv = rotation_matrix*[(1,-1),(-1,1)]
        dd = np.sign(microns_per_pixel_scale)
        rotation_matrix_inv = np.dot(rotation_matrix*[(1,-1),(-1,1)], [(dd[0], 0), (0, dd[1])])
        for ii in range(segworm.shape[0]):
            segworm[ii] = np.dot(rotation_matrix_inv, segworm[ii].T).T
        segworm_x = segworm[:,:,0]
        segworm_y = segworm[:,:,1]
        
        frame_annotations = fvars['info'].video.annotations.frames
        
        #%%
        max_n_skel = min(segworm_x.shape[0], skeletons.shape[0])
        #%%
        seg_x = segworm_x.copy()
        seg_y = segworm_y.copy()
                
        skel_x = skeletons[:,:,0];
        skel_y = skeletons[:,:,1];
        
        dXo = skel_x[:max_n_skel] - seg_x[:max_n_skel]
        dYo = skel_y[:max_n_skel] - seg_y[:max_n_skel]
        
        shift_x = np.nanmedian(dXo)
        shift_y = np.nanmedian(dYo)
        
        seg_x += shift_x
        seg_y += shift_y
        #%%
        
        dX = skel_x[:max_n_skel] - seg_x[:max_n_skel] 
        dY = skel_y[:max_n_skel] - seg_y[:max_n_skel] 
        R_error = dX*dX + dY*dY
        
        skel_error = np.sqrt(np.mean(R_error, axis=1))
                
        print('S', shift_x, shift_y)
        #%%
        if True:
            w_xlim = w_ylim = (-10, skel_error.size+10)
            plt.figure()
            plt.subplot(3,1,1)
            plt.plot(skel_error, '.')
            plt.ylim((0, np.nanmax(skel_error)))
            plt.xlim(w_xlim)
            plt.title(mask_id)
            plt.ylabel('Error')
            
            plt.subplot(3,1,2)
            plt.plot(skel_y[:,1], 'b')
            plt.plot(seg_y[:,1], 'r')
            plt.xlim(w_ylim)
            plt.ylabel('Y coord')
            
            plt.subplot(3,1,3)
            plt.plot(skel_x[:,1], 'b')
            plt.plot(seg_x[:,1], 'r')
            plt.xlim(w_xlim)
            plt.ylabel('X coord')
            plt.xlabel('Frame Number')
            
            plt.figure()
            delT = 15
            #plt.subplot(3,1,1)
            plt.plot(skel_x[::delT].T, skel_y[::delT].T, 'b')    
            plt.plot(seg_x[::delT].T, seg_y[::delT].T, 'r')
            plt.axis('equal')
            plt.title(mask_id)

    #%%
        if False:
            tt = 4040#6250
            plt.figure()
            plt.plot(skel_x[tt], skel_y[tt], 'b')
            plt.plot(segworm_x[tt], segworm_y[tt], 'r')
            plt.plot(seg_x[tt], seg_y[tt], 'm')
            plt.axis('equal')
        #%%
        #for kk in range(-1000, 1000):
        #    plt.plot(segworm_x[tt+kk], segworm_y[tt+kk], 'r')
        
        
        #for kk in range(-1000, 1000):
        #    plt.plot(skel_x[tt+kk], skel_y[tt+kk], 'b')
        
        #dd = np.stack((skel_x[tt], skel_y[tt]), axis = 1)
        #dd = (dd+stage_vec_ori[tt])/micronsPerPixel*np.dot(rotation_matrix_inv, micronsPerPixel)
        #dd -= stage_vec_ori[tt]
        #plt.plot(dd[:,0], dd[:,1], 'c')
        
        #dd = np.stack((skel_x[tt], skel_y[tt]), axis = 1)
        #dd = (dd+stage_vec_ori[tt])/micronsPerPixel*np.dot(rotation_matrix, micronsPerPixel)
        #dd -= stage_vec_ori[tt]
        #plt.plot(dd[:,0], dd[:,1], 'g')
        
        
    #%%
        #import pandas as pd
        #with pd.HDFStore(masked_image_file, 'r') as fid:
        #    stage_log = fid['/stage_log']
        #stage_log['stage_x']
    #%%
        #with tables.File(skeletons_file, 'r') as fid:
        #    stage_vec_ori = fid.get_node('/stage_movement/stage_vec')[:]