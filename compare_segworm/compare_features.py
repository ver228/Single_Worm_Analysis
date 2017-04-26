#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 11:39:21 2017

@author: ajaver
"""

import os
import glob
import numpy as np
import matplotlib.pylab as plt
from matplotlib.backends.backend_pdf import PdfPages

from read_feats import FeatsReaderComp, FEATS_OW_MAP

from tierpsy.helper.misc import get_base_name
#%%
def plot_indv_feat(feats1, feats2, field, add_name=True, is_hist=False):
    xx = feats1[field]
    yy = feats2[field]
    
    tot = min(xx.size, yy.size)
    xx = xx[:tot]
    yy = yy[:tot]
    
    
    if is_hist:
        xx = xx[~np.isnan(xx)]
        yy = yy[~np.isnan(yy)]
        
        bot = min(np.min(xx), np.min(yy))
        top = max(np.max(xx), np.max(yy))
        
        bins = np.linspace(bot, top, 100)
        
        count_x, _ = np.histogram(xx, bins)
        count_y, _ = np.histogram(yy, bins)
        
        l1 = plt.plot(bins[:-1], count_x)
        l2 = plt.plot(bins[:-1], count_y)
        if add_name:
            my = max(np.max(count_x), np.max(count_y))*0.95
            mx = bins[1]
            plt.text(mx, my, field)
            #plt.title(field)
        return (l1, l2)
    else:
        ll = plt.plot(xx, yy, '.', label=field)
        ran1 = plt.ylim()
        ran2 = plt.xlim()
        
        ran_l = ran1 if np.diff(ran1) < np.diff(ran2) else ran2
        
        plt.plot(ran_l, ran_l, 'k--')
        if add_name:
            my = (ran1[1]-ran1[0])*0.97 + ran1[0]
            mx = (ran2[1]-ran2[0])*0.03 + ran2[0]
            plt.text(mx, my, field)
        
        return ll
        #plt.legend(handles=ll, loc="lower right", fancybox=True)
        #plt.axis('equal')
#%%

def plot_feats_comp(feats1, feats2, is_hist=False):
    
    tot_f1 = max(feats1[x].size for x in feats1)
    tot_f2 = max(feats2[x].size for x in feats2)
    tot = min(tot_f1, tot_f2)
    
    fields = set(feats1.keys()) & set(feats2.keys())
    ii = 0
    
    sub1, sub2 = 5, 6
    tot_sub = sub1*sub2
    
    all_figs = []
    for field in sorted(fields):
        if feats1[field].size == 1 or feats2[field].size == 1:
            continue
        
        if is_hist and \
        not (feats1[field].size >= tot and feats2[field].size >= tot):
            continue
        
            
        if ii % tot_sub == 0:
            fig = plt.figure(figsize=(14,12))
            all_figs.append(fig)
            
        sub_ind = ii%tot_sub + 1
        ii += 1
        plt.subplot(sub1, sub2, sub_ind)
        
        
        plot_indv_feat(feats1, feats2, field, is_hist)
        
    
    return all_figs
#%%
def save_features_pdf(feat_file, 
                      segworm_feat_file, 
                      save_plot_dir,
                      feats2plot=None):
    
    basename = get_base_name(feat_file)
    pdf_file = os.path.join(save_plot_dir, basename + '_feat_comparison.pdf')
    feats_reader = FeatsReaderComp(feat_file, segworm_feat_file)
    tierpsy_feats = feats_reader.read_plate_features()
    segworm_feats = feats_reader.read_feats_segworm()
    
    
    rev_dict = {val:key for key,val in FEATS_OW_MAP.items()}
    
    if feats2plot is None:
        feats2plot = [val for key,val in FEATS_OW_MAP.items()]
    else:
        if not any('.' in x for x in feats2plot):
            feats2plot = [FEATS_OW_MAP[x] for x in feats2plot]
            
    feats2plot = sorted(feats2plot)
    with PdfPages(pdf_file) as pdf_id:
        for ow_field in feats2plot:
            #if not 'locomotion.crawling_bends' in ow_field:
            #    continue 
            field = rev_dict[ow_field]
            if tierpsy_feats[field].size == 1 or segworm_feats[field].size == 1:
                continue
            
            plt.figure(figsize=(10,5))
            plt.subplot(1,2,1)
            plot_indv_feat(tierpsy_feats, segworm_feats, field, add_name=False, is_hist=False)
            plt.xlabel('tierpsy features')
            plt.ylabel('segworm features')
            
            
            plt.subplot(1,2,2)
            ax = plot_indv_feat(tierpsy_feats, segworm_feats, field, add_name=False, is_hist=True)
            L=plt.legend(ax)
            for ii, ff in enumerate(('tierpsy features', 'segworm features')):
                L.get_texts()[ii].set_text(ff)
            
            plt.suptitle(ow_field)
            pdf_id.savefig()
            plt.close()

    return tierpsy_feats, segworm_feats

if __name__ == '__main__':
    #%%

    
    #main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    #skel_file = os.path.join(main_dir, base_name + '_skeletons.hdf5')
    #feat_file = os.path.join(main_dir, base_name + '_features.hdf5')
    #segworm_feat_file = os.path.join(main_dir, '_segworm_files', base_name + '_features.mat')
    
    save_plot_dir = os.path.join('.', 'plots', 'original')
    if not os.path.exists(save_plot_dir):
        os.makedirs(save_plot_dir)
    
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Ev_L4 worms/Results'
    feat_files = glob.glob(os.path.join(main_dir, '**', '*_features.hdf5'), recursive=True)
    
    
    #feats2plot = set(sum(map(list, FEATS2SWITCH), []))
    feats2plot = None
    for feat_file in feat_files:
        print(feat_file)
        skel_file = feat_file.replace('_features.hdf5', '_skeletons.hdf5')
        segworm_feat_file = feat_file.replace('.hdf5', '.mat').replace('Results','RawVideos')
        tierpsy_feats, segworm_feats = \
        save_features_pdf(feat_file, 
                          segworm_feat_file, 
                          save_plot_dir,
                          feats2plot=feats2plot)
    


