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
#fname = '/Volumes/behavgenom_archive$/Avelino/screening/CeNDR/MaskedVideos/CeNDR_Set4_251017/N2_worms10_food1-10_Set9_Pos4_Ch3_25102017_153032.hdf5'
fname = '/Users/ajaver/OneDrive - Imperial College London/mutliworm_example/BRC20067_worms10_food1-10_Set2_Pos5_Ch2_02062017_121709.hdf5'

with tables.File(fname, 'r') as fid, tables.File('single_mask.hdf5', mode='w') as fid_m:
    img = fid.get_node('/full_data')[0]
    
    node = fid.get_node('/mask')
    mask = node[0]
    print(node.shape)
    
    fid_m.create_carray('/', 'mask', obj=mask[None, ...], 
                        chunkshape=(1,*node.shape[1:]),
                        atom=node.atom, filters=node.filters)
    
#plt.imshow(img, cmap='gray', interpolation='none')    
cv2.imwrite('full_frame.bmp', img)
cv2.imwrite('mask_frame.bmp', mask)


#%%
#img_reduced = img[840:960, 850:940]
#mask_reduced = mask[1430:1515, 1060:1130]
mask_reduced = mask[1310:1380, 330:440]

plt.figure()
plt.imshow(mask)

plt.figure()
plt.imshow(mask_reduced)

cv2.imwrite('mask_reduced.bmp', mask_reduced)

#22494 frames | compressed file 984M | 90.0638671875 GB expected full
#%% 44.8 kb
for kk in [100, 95, 90, 85, 80, 60, 10, 0]:#range(0, 101, 10):
    cv2.imwrite('comp_{:03}.jpg'.format(kk), img, [int(cv2.IMWRITE_JPEG_QUALITY), kk])

#%%
fnames = ['full_frame.bmp', 'comp_095.jpg', 'comp_060.jpg',  'comp_010.jpg', 'single_mask.hdf5']

import os

plt.figure(figsize = (6, 20))

for ii, ff in enumerate(fnames):
    if ff.endswith('.hdf5'):
        ss = 'HDF5 gzip'
        with tables.File(ff) as fid:
            img = fid.get_node('/mask')[0]
        
    elif ff.endswith('.bmp'):
        ss = 'Raw Image'
        img = cv2.imread(ff)
    else:
        cc = int(ff.split('_')[-1][:-4])
        ss = 'JPG quality: {}'.format(cc)
        img = cv2.imread(ff)
        
    st = os.stat(ff)
        
    
    
    plt.subplot(5,1, ii+1)
    plt.imshow(img[1310:1380, 330:440], 
               interpolation=None, cmap='gray', 
               vmin=0, vmax=255)
    plt.axis('off')
    ss = '{}\n{:.1f}kb'.format(ss, st.st_size/1000)
    plt.annotate(ss, xy=(106, 14), 
                 size = 15, color='w',
                 horizontalalignment='right')
    
plt.savefig('JPG_compression.pdf', bbox_inches='tight')
    