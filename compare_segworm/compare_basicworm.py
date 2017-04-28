#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import numpy as np
import open_worm_analysis_toolbox as mv
from read_feats import FeatsReaderComp, FEATS_OW_MAP
from compare_features import plot_feats_comp

if __name__ == '__main__':
    #%%
    #main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    #skel_file = os.path.join(main_dir, base_name + '_skeletons.hdf5')
    #feat_file = os.path.join(main_dir, base_name + '_features.hdf5')
    #segworm_feat_file = os.path.join(main_dir, '_segworm_files', base_name + '_features.mat')
    
#    save_plot_dir = os.path.join('.', 'plots', 'original')
#    if not os.path.exists(save_plot_dir):
#        os.makedirs(save_plot_dir)
    
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Ev_L4 worms/Results'
    feat_files = glob.glob(os.path.join(main_dir, '**', '*_features.hdf5'), recursive=True)
    
    
    #feats2plot = set(sum(map(list, FEATS2SWITCH), []))
    feats2plot = None
    for feat_file in feat_files:
        print(feat_file)
        
    segworm_feat_file = feat_file.replace('.hdf5', '.mat').replace('Results','RawVideos')
    feats_reader = FeatsReaderComp(feat_file, segworm_feat_file)
    
    skeletons, skel_segworm = feats_reader.read_skeletons()
    segworm_feats = feats_reader.read_feats_segworm()
    
    skel_segworm = np.rollaxis(skel_segworm, 0, 3)
    bw_mat = mv.BasicWorm.from_skeleton_factory(skel_segworm);
    nw_mat = mv.NormalizedWorm.from_BasicWorm_factory(bw_mat)
    wf_mat = mv.WormFeatures(nw_mat)
    #%%
    ow_mat = {}
    for key,val in FEATS_OW_MAP.items():
        if val in wf_mat._features:
            ow_mat[key] = wf_mat._features[val].value
    #%%
    plot_feats_comp(ow_mat, segworm_feats, is_hist=False)