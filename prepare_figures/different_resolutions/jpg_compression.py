#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 15:46:38 2018

@author: ajaver
"""

import cv2
import matplotlib.pylab as plt

import tables
#fname = '/Volumes/behavgenom_archive$/Avelino/screening/CeNDR/MaskedVideos/CeNDR_Set1_020617/N2_worms10_food1-10_Set3_Pos4_Ch3_02062017_123419.hdf5'
#fname = '/Volumes/behavgenom_archive$/Avelino/screening/CeNDR/MaskedVideos/CeNDR_Set1_020617/JU775_worms5_food1-10_Set2_Pos5_Ch4_02062017_121656.hdf5'
fname = '/Volumes/behavgenom_archive$/Avelino/screening/CeNDR/MaskedVideos/CeNDR_Set4_251017/N2_worms10_food1-10_Set9_Pos4_Ch3_25102017_153032.hdf5'
with tables.File(fname, 'r') as fid:
    img = fid.get_node('/full_data')[0]
    print(fid.get_node('/mask').shape)
#plt.imshow(img, cmap='gray', interpolation='none')    
cv2.imwrite('full_frame.bmp', img)

#22494 frames | compressed file 984M | 90.0638671875 GB expected full
#%% 44.8 kb
for kk in range(0, 101, 10):
    cv2.imwrite('comp_{:03}.jpg'.format(kk), img, [int(cv2.IMWRITE_JPEG_QUALITY), kk])

#%%
fnames = ['full_frame.bmp', 'comp_100.jpg', 'comp_060.jpg',  'comp_010.jpg',]

import os

plt.figure(figsize = (16, 6))

for ii, ff in enumerate(fnames):
    if ff.endswith('.bmp'):
        ss = 'Raw Image'
    else:
        cc = int(ff.split('_')[-1][:-4])
        ss = 'JPG quality: {}'.format(cc)
        
    st = os.stat(ff)
        
    img = cv2.imread(ff)
    
    plt.subplot(1,4, ii+1)
    plt.imshow(img[840:960, 850:940], interpolation=None, cmap='gray')
    plt.axis('off')
    plt.title('{}\n{:.1f}kb'.format(ss, st.st_size/1024))
    
plt.savefig('JPG_compression.pdf', bbox_inches='tight')
    