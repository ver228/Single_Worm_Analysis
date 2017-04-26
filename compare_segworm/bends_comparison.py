#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 17:35:48 2017

@author: ajaver
"""
import glob
import os
import matplotlib.pylab as plt
import numpy as np
import tables
from matplotlib.backends.backend_pdf import PdfPages

from tierpsy.helper.params import read_microns_per_pixel
from tierpsy.helper.misc import get_base_name

from read_feats import FeatsReaderComp
from compare_features import plot_indv_feat

def read_data(feat_file, segworm_feat_file):
    microns_per_pixel = read_microns_per_pixel(feat_file)
    feats_reader = FeatsReaderComp(feat_file, segworm_feat_file)
    tierpsy_feats = feats_reader.read_plate_features()
    segworm_feats = feats_reader.read_feats_segworm()
    
    skeletons, skel_segworm = feats_reader.read_skeletons()
    stage_movement = feats_reader.stage_movement
    
    tot = min(skeletons.shape[0], skel_segworm.shape[0])
    skeletons_pix = (skeletons[:tot] - stage_movement[:tot, np.newaxis, :])/microns_per_pixel
    skel_segworm_pix = (skel_segworm[:tot] - stage_movement[:tot, np.newaxis, :])/microns_per_pixel
    
    return tierpsy_feats, segworm_feats, skeletons_pix, skel_segworm_pix

def process_file(feat_files, pdf_file):
    
    segworm_feat_file = feat_file.replace('.hdf5', '.mat').replace('Results','RawVideos')
    mask_file = feat_file.replace('_features.hdf5', '.hdf5').replace('Results','MaskedVideos')
    
    
    tierpsy_feats, segworm_feats, skeletons_pix, skel_segworm_pix = read_data(feat_file, segworm_feat_file)
    
    feat_name = 'tail_bend_sd'
    n_skel_plot = 10
    
    ow_feat = tierpsy_feats[feat_name]
    mat_feat = segworm_feats[feat_name]
    
    tot =skeletons_pix.shape[0]
    ow_feat = ow_feat[:tot]
    mat_feat = mat_feat[:tot]
     
    with PdfPages(pdf_file) as pdf_id:
        plt.figure()
        plot_indv_feat(tierpsy_feats, segworm_feats, feat_name)
        pdf_id.savefig()
            
        dd = np.abs(np.abs(ow_feat)-np.abs(mat_feat))
        nn = np.argsort(dd)
        
        good = ~np.isnan(dd[nn])
        nn = nn[good]
        for frame_number in nn[-n_skel_plot:]:
            with tables.File(mask_file, 'r') as fid:
                img = fid.get_node('/mask')[frame_number]
            
            plt.figure()
            ax = plt.subplot(1,1,1)
            plt.imshow(img, interpolation='none', cmap='gray')
            plt.grid('off')
            
            xx = skeletons_pix[frame_number, :, 0]
            yy = skeletons_pix[frame_number, :, 1]
            l1, = plt.plot(xx,yy, label="tierpsy")
            
            xx = skel_segworm_pix[frame_number, :, 0]
            yy = skel_segworm_pix[frame_number, :, 1]
            l2, = plt.plot(xx,yy, label="segworm")
            
            X = np.mean(xx)
            plt.xlim((X-100, X+100))
            Y = np.mean(yy)
            plt.ylim((Y-100, Y+100))
            
            val_tierpsy = ow_feat[frame_number]
            val_segworm = mat_feat[frame_number]
            
            plt.title('tierpsy: {0:2.2f} segworm: {1:2.2f}'.format(val_tierpsy, val_segworm))
            
            
            handles, labels = ax.get_legend_handles_labels()
            l = ax.legend(handles, labels)
            for text in l.get_texts():
                text.set_color("white")
            
            pdf_id.savefig()
            



if __name__ == '__main__':
    #main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    #feat_files = glob.glob(os.path.join(main_dir, '*_features.hdf5'))
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Ev_L4 worms/Results'
    feat_files = glob.glob(os.path.join(main_dir, '**', '*_features.hdf5'), recursive=True)
    
    
    
    for feat_file in feat_files:
        save_plot_dir = os.path.join('.', 'plots', 'original')
        if not os.path.exists(save_plot_dir):
            os.makedirs(save_plot_dir)
        basename = get_base_name(feat_file)
        pdf_file = os.path.join(save_plot_dir, basename + '_tail_bend_sd.pdf')
        process_file(feat_files, pdf_file)
    
    
    
    
    
    
    
    
    
    
    
    