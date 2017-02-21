#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 18:35:13 2017

@author: ajaver
"""
import os
import tables
import numpy as np
from scipy.io import loadmat

def get_skels(feat_file):
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
        
def get_skels_segworm(segworm_feat_file):
    #load segworm data
    fvars = loadmat(segworm_feat_file, struct_as_record=False, squeeze_me=True)
    segworm_x = -fvars['worm'].posture.skeleton.x.T
    segworm_y = -fvars['worm'].posture.skeleton.y.T
    segworm = np.stack((segworm_x,segworm_y), axis=2)
    
    return segworm

main_dir = '/Users/ajaver/OneDrive - Imperial College London/Tests/feats/'
#base_name = 'N2 on food L_2011_03_22__13_01_52___1___6'
base_name = 'N2 on food R_2011_09_22__11_50_45___2___3'

segworm_feat_file = os.path.join(main_dir, base_name + '_features.mat')
feat_file = os.path.join(main_dir, base_name + '_features.hdf5')
skel_file = os.path.join(main_dir, base_name + '_skeletons.hdf5')

skeletons = get_skels(feat_file)
skel_segworm = get_skels_segworm(segworm_feat_file)


#load rotation matrix to compare with the segworm
with tables.File(skel_file, 'r') as fid:
    rotation_matrix = fid.get_node('/stage_movement')._v_attrs['rotation_matrix']


microns_per_pixel_scale = fid.get_node(
        '/stage_movement')._v_attrs['microns_per_pixel_scale']

# let's rotate the stage movement
dd = np.sign(microns_per_pixel_scale)
rotation_matrix_inv = np.dot(
    rotation_matrix * [(1, -1), (-1, 1)], [(dd[0], 0), (0, dd[1])])

skel_segworm = -np.dot(rotation_matrix_inv, skel_segworm.T).T

#%%
import matplotlib.pylab as plt

tt = 0
xx = skeletons[tt, :, 0]
yy = skeletons[tt, :, 1]
plt.plot(xx, yy, 'o-')
xx = skel_segworm[tt, :, 0]
yy = skel_segworm[tt, :, 1]
plt.plot(xx, yy, 'o-r')


