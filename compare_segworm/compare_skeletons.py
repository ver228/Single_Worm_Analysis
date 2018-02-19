#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 14:15:22 2017

@author: ajaver
"""
import os
import glob
import numpy as np
import matplotlib.pylab as plt
from matplotlib.backends.backend_pdf import PdfPages

from read_feats import FeatsReaderComp

def plot_skel_diff(skeletons, skel_segworm):
    #%%
    max_n_skel = min(skel_segworm.shape[0], skeletons.shape[0])
    delS = skeletons[:max_n_skel]-skel_segworm[:max_n_skel]
    R_error = delS[:,:,0]**2 + delS[:,:,1]**2
    skel_error = np.sqrt(np.mean(R_error, axis=1))
    #%%   
        
    w_xlim = w_ylim = (-10, skel_error.size+10)
    plt.figure(figsize=(15, 5))
    plt.subplot(3,3,1)
    
    plt.plot(skel_error, '.')
    plt.ylim((0, np.nanmax(skel_error)))
    plt.xlim(w_xlim)
    plt.title('')
    plt.ylabel('RMSE [mm]')
    
    plt.subplot(3,3,4)
    plt.plot(skeletons[:,1, 0], color='darkolivegreen', lw=3)
    plt.plot(skel_segworm[:,1, 0], color='tomato')
    plt.xlim(w_ylim)
    plt.ylabel('Y coord [mm]')
    
    plt.subplot(3,3,7)
    plt.plot(skeletons[:,1, 1], color='darkolivegreen', lw=3)
    plt.plot(skel_segworm[:,1, 1], color='tomato')
    plt.xlim(w_xlim)
    plt.ylabel('X coord [mm]')
    plt.xlabel('Frame Number')
    
    #plt.figure()
    delT = 1
    plt.subplot(1,3,2)
    plt.plot(skeletons[::delT, 25, 0].T, skeletons[::delT, 25, 1].T, color='darkolivegreen', lw=3)
    #plt.axis('equal')    
    
    #plt.subplot(1,2,2)
    plt.plot(skel_segworm[::delT, 25, 0].T, skel_segworm[::delT, 25, 1].T, color='tomato')
    
    tt = 2500
    plt.plot(skel_segworm[tt, 25, 0].T, skel_segworm[tt, 25, 1].T, 'ok', 
             markersize = 12, markerfacecolor=None, alpha=0.3, markeredgecolor='black', markeredgewidth=3)
    
    
    plt.axis('equal') 
    #%%
    plt.subplot(1,3,3)
    plt.plot(skeletons[tt, :, 0].T, skeletons[tt, :, 1].T, 'o', color='darkolivegreen', markersize=6)
    plt.plot(skeletons[tt, 0, 0].T, skeletons[tt, 0, 1].T, '^', color='darkolivegreen', markersize=10)
    plt.plot(skel_segworm[tt, :, 0].T, skel_segworm[tt, :, 1].T, 'o', color='tomato', markersize=4)
    plt.plot(skel_segworm[tt, 0, 0].T, skel_segworm[tt, 0, 1].T, 'v', color='tomato', markersize=8)

    #ax.set_ylim((-29.2, -28.2))
    #ax.set_xlim((-28.2, -27.2))
    
    plt.axis('equal') 
    #%%
    
    
    
    
    
    
    
if __name__ == '__main__':
    #main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    #feat_files = glob.glob(os.path.join(main_dir, '*_features.hdf5'))
    #main_dir = '/Users/ajaver/OneDrive - Imperial College London/Ev_L4 worms/Results_anticlockwise'
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Ev_videos/N2_L4/Results/'
    feat_files = glob.glob(os.path.join(main_dir, '**', '*_features.hdf5'), recursive=True)
    
    save_plot_dir = os.path.join('.', 'plots')
    if not os.path.exists(save_plot_dir):
        os.makedirs(save_plot_dir)
    
    pdf_file = os.path.join(save_plot_dir, 'skeletons_comparison.pdf')
    
    #with PdfPages(pdf_file) as pdf_id:
    for feat_file in feat_files:
        fname = os.path.basename(feat_file)
        print(fname)
        
        #dd = fname.rpartition('.')[0] + '.mat'
        #segworm_feat_file = os.path.join(main_dir, '_segworm_files', dd)
        
        segworm_feat_file = feat_file.replace('.hdf5', '.mat').replace('Results','RawVideos')
        feats_reader = FeatsReaderComp(feat_file, segworm_feat_file)
        
        skeletons, skel_segworm = feats_reader.read_skeletons()
        plot_skel_diff(-skeletons/1000, -skel_segworm/1000)
        #plt.suptitle(fname.replace('_features.hdf5', ''))
        
        plt.tight_layout()
        plt.savefig(fname.replace('_features.hdf5', '.pdf'))
        #plt.close()
        break
