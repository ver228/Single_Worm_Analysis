#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 15:11:10 2017

@author: ajaver
"""
import fnmatch
import os
import matplotlib.pylab as plt
import glob
from tierpsy.analysis.feat_create.obtainFeaturesHelper import WormFromTable
from feat_helper import read_feats_segworm, read_ow_feats, plot_feats_comp, _plot_indv_feat
import open_worm_analysis_toolbox as mv

import multiprocessing as mp

def _get_feats(feat_mat_file):
        base_name = os.path.basename(feat_mat_file).replace('_features.mat', '')
        skel_file = os.path.join(main_dir, base_name + '_skeletons.hdf5')
        
        print(base_name)
        
        worm = WormFromTable(skel_file, 1)
        worm.correct_schafer_worm()
        worm_openworm = worm.to_open_worm()
        
        assert worm_openworm.skeleton.shape[1] == 2
        wf = mv.WormFeatures(worm_openworm)
        
        feats_mat = read_feats_segworm(feat_mat_file)
        feats_ow = read_ow_feats(wf)
        return (base_name, feats_mat, feats_ow)

if __name__ == '__main__':
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    
    flist = glob.glob(os.path.join(main_dir, "N2*_features.mat"))
    
    n_batch = mp.cpu_count()
    p = mp.Pool(n_batch)
    feats = p.map(_get_feats, flist)
    #feats = _get_feats(flist[0])
    #asfsadf
    #%%
    good_matches = [
            'amplitude_ratio',
            'area',
            'area_length_ratio',
            'eccentricity',
            '*_bend_mean',
            '*_bend_sd',
            '*_speed',
            '*_width',
            'length',
            'width_length_ratio',
            'max_amplitude',
            'track_length',
            '*_wavelength',
            'path_range'
            ]
    
    bad_matches = [
            'foraging_speed'
            ]
    
    def _is_good(x):
        good = any(fnmatch.fnmatch(x, gg) for gg in good_matches)
        bad = any(fnmatch.fnmatch(x, gg) for gg in bad_matches)
        return good and not bad
    #%%
    for base_name, feats_mat, feats_ow in feats:
        feats_ow = {x:feats_ow[x] for x in feats_ow if not _is_good(x)} 
        #{x:feats_mat[x] for x in feats_mat if any(ff in x for ff in ('head_width'))}
        all_figs = plot_feats_comp(feats_ow, feats_mat, is_correct=True)
        for fig in all_figs:
            plt.suptitle(base_name)
        break
        
        
    #%%
    from feat_helper import FEATS_MAT_MAP, FEATS_OW_MAP
    
    bad_feats = {x:FEATS_MAT_MAP[x] for x in FEATS_MAT_MAP if  not _is_good(x)}
    #%%
    for key, val in bad_feats.items():
        print(val.replace('/', '.')[1:])
    
    #%%
    '''
    path.range has a very straight forward calculation, it seems wrong in segworm...
    range -3 to 3??
    
    '''
    
    field = 'path_range'
    plt.figure()
    plt.subplot(1,2,1)
    plt.plot(feats_ow['path_curvature'])
    plt.subplot(1,2,2)
    plt.plot(feats_mat['path_range'])
    plt.suptitle(field)

    #%%
    
    xx = feats_ow['path_curvature']
    yy = feats_mat['path_range']
    ax = plt.subplot(1,1,1)
    ax.scatter(xx,yy)
    
    #%%
    #%%
#    import numpy as np
#    def _nanhist(xx, nbins = 100):
#        feats_mat[field]; plt.hist(xx[~np.isnan(xx)], nbins)
#    field = 'path_range'
#    plt.figure()
#    plt.subplot(1,2,1)
#    _nanhist(feats_ow[field], nbins = 100)
#    plt.subplot(1,2,2)
#    _nanhist(feats_mat[field], nbins = 100)
#    plt.suptitle(field)
    
    
    
    
    
    
    
    
    