#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import numpy as np
import open_worm_analysis_toolbox as mv
import matplotlib.pylab as plt

from tierpsy.helper.misc import get_base_name

from read_feats import FeatsReaderComp, FEATS_OW_MAP
from compare_features import save_features_pdf

if __name__ == '__main__':
    save_plot_dir = os.path.join('.', 'plots', 'from_basicworm')
    if not os.path.exists(save_plot_dir):
        os.makedirs(save_plot_dir)
        
    root_dir = '/Users/ajaver/OneDrive - Imperial College London/Ev_videos/N2_L4/'
    
    results_dir = os.path.join(root_dir, 'Results_clockwise')
    raw_dir = os.path.join(root_dir, 'RawVideos')
    feat_files = glob.glob(os.path.join(results_dir, '**', '*_features.hdf5'), recursive=True)
    
    

    #feats2plot = set(sum(map(list, FEATS2SWITCH), []))
    
    
    feats2plot = None
    for feat_file in feat_files[1:]:
        print(feat_file)
        basename = get_base_name(feat_file)
        
        
        
        segworm_feat_file = feat_file.replace(results_dir, raw_dir).replace('.hdf5', '.mat')
        pdf_file1 = os.path.join(save_plot_dir, basename + '_segworm_openworm.pdf')
        pdf_file2 = os.path.join(save_plot_dir, basename + '_tierpsy_openworm.pdf')
        feats_reader = FeatsReaderComp(feat_file, segworm_feat_file)
       
        skeletons, skel_segworm = feats_reader.read_skeletons()
        segworm_feats = feats_reader.read_feats_segworm()
        tierpsy_feats = feats_reader.read_plate_features()
        
        
        skel_segworm = np.rollaxis(skel_segworm, 0, 3)
        bw_mat = mv.BasicWorm.from_skeleton_factory(skel_segworm);
        nw_mat = mv.NormalizedWorm.from_BasicWorm_factory(bw_mat)
        #nw_mat.video_info.ventral_mode = 2
        
        wf_mat = mv.WormFeatures(nw_mat)
        
        ow_mat = {}
        for key,val in FEATS_OW_MAP.items():
            if val in wf_mat._features:
                ow_mat[key] = wf_mat._features[val].value
                
        #%%
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(ow_mat['backward_distance'])
        plt.plot(segworm_feats['backward_distance'])
        plt.subplot(2,1,2)
        plt.plot(ow_mat['forward_distance'])
        plt.plot(segworm_feats['forward_distance'])
        #%%
        break
        #%%
#        save_features_pdf(segworm_feats, 
#                          ow_mat, 
#                          pdf_file1, 
#                          xlabel='segworm feats',
#                          ylabel='openworm feats on segworm skels')
#        save_features_pdf(tierpsy_feats, 
#                          ow_mat,
#                          pdf_file2,
#                          xlabel='tierpsy feats',
#                          ylabel='openworm feats on segworm skels')
        
        
#
#    
#    #%%
##    plt.plot(segworm_feats['midbody_speed'])
##    plt.plot(ow_mat['midbody_speed'])
##%%
#for key in segworm_feats:
#    if 'inter' in key:
#        print(key, segworm_feats[key],ow_mat[key])

#%%
