#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 22:05:12 2018

@author: ajaver
"""

from tierpsy.helper.params import read_microns_per_pixel
import pandas as pd
import tables
import glob
import os
import numpy as np

import matplotlib.pylab as plt

#fname = '/Users/ajaver/OneDrive - Imperial College London/aggregation/N2_1_Ch1_29062017_182108_comp3.hdf5'
#print(read_microns_per_pixel(fname))
#
#fname = '/Users/ajaver/OneDrive - Imperial College London/Ev_videos/N2_adults/MaskedVideos/N2_A_24C_L_5_2015_06_16__19_54_27__.hdf5'
#print(read_microns_per_pixel(fname))

main_dir = '/Users/ajaver/OneDrive - Imperial College London/Ev_videos/diff_resolutions/Results'
#fnames = glob.glob(os.path.join(main_dir, '*_features.hdf5'))

#ext_s = '_featuresN.hdf5'
ext_s = '_features.hdf5'
field_n = '/features_timeseries'

fnames = glob.glob(os.path.join(main_dir, '*' + ext_s))
#%%
plt.figure()
feats = {}
masks = {}
bn_k = {'N2_45':'45x34',
        'N2_91':'91x68',
        'N2_213':'213x160',
        'N2_640':'640x480'
        }

scale_k = {}

for fname in fnames:
    bn = os.path.basename(fname)
    bn = bn.replace(ext_s, '')
    with pd.HDFStore(fname, 'r') as fid:
        if not bn in bn_k:
            continue
        
        #feats[bn] = fid['/timeseries_data']
        if field_n in fid:
            feats[bn_k[bn]] = fid[field_n]
    
    f_skel = fname.replace(ext_s, '_skeletons.hdf5')
    if os.path.exists(f_skel):
        with tables.File(f_skel, 'r') as fid:
            skel = fid.get_node('/skeleton')[1000]
    else:
        skel = None

    ff = fname.replace(ext_s, '.hdf5').replace('Results', 'MaskedVideos')
    with tables.File(ff, 'r') as fid:
        img = fid.get_node('/mask')[1000]
        microns_per_pixel = read_microns_per_pixel(ff)
        
      
        
    masks[bn_k[bn]] = (microns_per_pixel, img, skel)
#%%

plt.figure(figsize = (12, 10))

bgnd_pix = 187
ll = ['45x34', '91x68', '213x160', '640x480'][::-1]
for i_k, k in enumerate(ll):
    (microns_per_pixel, img, skel) = masks[k]
    pix = int(k.split('x')[0])
    l_scale = 300/microns_per_pixel
    
    n_scale = pix/640
    x_cc = 500*n_scale
    y_cc = 450*n_scale
    
    
    sc_t = '{:.1f} $\mu$m/pix'.format(microns_per_pixel)
    strT = '{} {}'.format(sc_t, k)
    
    img_c = img.copy()
    img_c[img_c==0] = bgnd_pix
    
    plt.subplot(2, 2, i_k+1)
    plt.imshow(img_c, interpolation=None, cmap='gray', vmin=0, vmax=255)
    plt.plot((x_cc, x_cc+l_scale), (y_cc,y_cc), 'w', linewidth=  3)
    
    if skel is not None:
        plt.plot(skel[:, 0], skel[:, 1], 'r', lw=1)
    
    plt.axis('off')
    plt.title(strT)
    
    scale_k[k] = sc_t
    
plt.savefig('scales.pdf')

        

#%%
#cols = feats['640x480'].columns[4:]
cols = ['length', 'foraging_speed', 'midbody_speed', 
        'head_bend_mean']

units = ['Length [$\mu$m]',
         'Foraging Speed [deg/s]', 
         'Midbody Speed [$\mu$m/s]', 
         'Mean Head Bend [deg]'
         #'Eigen Worm 1',
         #'Eigen Worm 6'
         ]


#cols = feats[bn].columns[2:-12]

#34x45

valid_keys = ['91x68', '213x160', '640x480']
#%%

tot_feats = len(cols)
#plt.figure(figsize=(10, 3))
f, axs = plt.subplots(tot_feats, 1, figsize=(10, 11), sharex=True)
for icol, col in enumerate(cols):  
    
    
    valid_keys = ['91x68', '213x160', '640x480']
    for ii, bn in enumerate(valid_keys):
        #plt.subplot(3,1, ii + 1)
        x = feats[bn]['timestamp'].values/25
        y = feats[bn][col].values
        axs[icol].plot(x, y)
        #axs[0].set_title(scale_k[bn], loc='left')
    #axs[icol].set_title(col, loc='left')
    axs[icol].set_ylabel(units[icol])
    axs[icol].get_yaxis().set_label_coords(-0.08,0.5)
    
    plt.xlim([4000, 8000])
    plt.suptitle(col)
    plt.savefig('{}_ts.pdf'.format(col))
    plt.tight_layout()
    #%%

plt.tight_layout()
plt.subplots_adjust(wspace=0, hspace=0)
plt.xlim([200, 250])
plt.xlabel('Time [s]')
#plt.suptitle(col)
plt.savefig('ts.pdf'.format(col))
#%%

f, axs = plt.subplots(tot_feats, 1, figsize=(4, 11))#, sharex=False, sharey=True)
for icol, col in enumerate(cols):  
    top = max(tab[col].max() for tab in feats.values())
    bot = min(tab[col].min() for tab in feats.values())
    #plt.figure(figsize=(3, 3))
    
    #plt.subplot(tot_feats, 1, icol+1)
    for bn in valid_keys[::-1]:
        cc, bin_edges = np.histogram(feats[bn][col], bins=100, range =(bot, top))
        axs[icol].plot(bin_edges[1:], cc, label=scale_k[bn])
    axs[icol].set_xlabel(units[icol])
    
#plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
axs[0].legend()


plt.subplots_adjust(wspace=0, hspace=0.3)

plt.tight_layout()
plt.savefig('hist.pdf'.format(col))
#plt.ylabel('Counts')

#%%
if False:
    #f, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True, sharex=True)
    #plt.subplot(1,2,2)
    xx = feats['640x480'][col]
    for ii, bn in enumerate(['91x68', '213x160']):
        plt.plot(xx, feats[bn][col], '.', label=scale_k[bn])
        plt.xlabel('640x480')
        #plt.ylabel(bn)
    
    plt.suptitle(col)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('{}_hist.pdf'.format(col))
    #%%
