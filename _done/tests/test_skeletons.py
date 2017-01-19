# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 21:57:30 2015

@author: ajaver
"""
import matplotlib.pylab as plt
import h5py
import pandas as pd
import cv2
import numpy as np
from skimage.filters import threshold_otsu
from scipy.signal import medfilt
import time
import os

from MWTracker.trackWorms.getSkeletonsTables import getWormMask, binaryMask2Contour, getWormROI
from MWTracker.trackWorms.segWormPython.cleanWorm import cleanWorm

file_mask = '/Users/ajaver/Desktop/Videos/Avelino_17112015/MaskedVideos/CSTCTest_Ch1_17112015_205616.hdf5'


file_skel = file_mask.replace('MaskedVideos', 'Results').replace('.hdf5', '_skeletons.hdf5')
file_traj = file_mask.replace('MaskedVideos', 'Results').replace('.hdf5', '_trajectories.hdf5')
assert(os.path.exists(file_mask))
assert(os.path.exists(file_traj))
assert(os.path.exists(file_skel))


with pd.HDFStore(file_skel, 'r') as fid:
    trajectories_data = fid['/trajectories_data']

#with pd.HDFStore(file_traj, 'r') as fid:
#    plate_worms = fid['/plate_worms']

current_frame = 400#2074#261
with h5py.File(file_mask, 'r') as fid:
    img = fid['/mask'][current_frame]

row_data = trajectories_data[trajectories_data['frame_number'] == current_frame]
row_data = row_data.iloc[0]


worm_img, roi_corner = getWormROI(img, row_data['coord_x'], row_data['coord_y'], row_data['roi_size'])
min_mask_area = row_data['area']/2

worm_mask, worm_cnt, _ = getWormMask(worm_img, row_data['threshold'], 10, min_mask_area)

#worm_cnt, _ = binaryMask2Contour(worm_mask, min_mask_area = min_mask_area)

#worm_cnt_n = cleanWorm(worm_cnt.astype(np.float), 49)
#worm_mask_n = np.zeros_like(worm_mask)
#cv2.drawContours(worm_mask_n, [worm_cnt_n.astype(np.int32)], 0, 1, -1)

plt.figure()
plt.imshow(worm_img, interpolation = 'none', cmap = 'gray')


plt.figure()
plt.imshow(worm_mask, interpolation = 'none', cmap = 'gray')
#plt.plot(worm_cnt[:,0], worm_cnt[:,1], 'r')
plt.xlim([0, worm_mask.shape[1]])
plt.ylim([0, worm_mask.shape[0]])
plt.grid('off')

#plt.figure()
#plt.imshow(worm_mask_n, interpolation = 'none', cmap = 'gray')
#plt.grid('off')


