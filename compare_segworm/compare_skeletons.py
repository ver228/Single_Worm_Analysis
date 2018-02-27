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
    
def main():
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
#%%
def main_single():    
    #%%
    #feat_file = '/Volumes/behavgenom_archive$/single_worm/finished/mutants/egl-47(n1081)V@MT2248/food_OP50/XX/30m_wait/anticlockwise/egl-47 (n1031)V on food R_2011_02_08__15_21___3___9_features.hdf5'
    #segworm_feat_file = '/Volumes/behavgenom$/Andre/Laura Grundy/egl-47/n1081/MT2248/on_food/XX/30m_wait/L/tracker_3/2011-02-08___15_21_00/egl-47 (n1031)V on food R_2011_02_08__15_21___3___9_features.mat'
    
#    feat_file = '/Volumes/behavgenom_archive$/single_worm/finished/mutants/unc-17(e245)IV@CB933/food_OP50/XX/30m_wait/anticlockwise/unc-17 (e245) on food R_2010_04_16__14_27___3___10_features.hdf5'
#    segworm_feat_file = '/Volumes/behavgenom$/Andre/Laura Grundy/unc-17/e245/CB933/on_food/XX/30m_wait/L/tracker_3/2010-04-16___14_27_00/unc-17 (e245) on food R_2010_04_16__14_27___3___10_features.mat'
    
#    feat_file = '/Volumes/behavgenom_archive$/single_worm/finished/mutants/unc-105(ok1432)II@RB1316/food_OP50/XX/30m_wait/anticlockwise/unc-105 (ok1432) on food R_2010_07_08__11_04_22___4___3_features.hdf5'
#    segworm_feat_file = '/Volumes/behavgenom$/Andre/Laura Grundy/unc-105/ok1432/RB1316/on_food/XX/30m_wait/L/tracker_4/2010-07-08___11_04_22/unc-105 (ok1432) on food R_2010_07_08__11_04_22___4___3_features.mat'
#    
#    feat_file = '/Volumes/behavgenom_archive$/single_worm/finished/WT/N2/food_OP50/XX/30m_wait/anticlockwise/n2 on food R_2010_01_14__10_34_06__1_features.hdf5'
#    segworm_feat_file = '/Volumes/behavgenom$/Andre/Laura Grundy/gene_NA/allele_NA/N2/on_food/XX/30m_wait/L/tracker_5/2010-01-14___10_34_06/n2 on food R_2010_01_14__10_34_06__1_features.mat'
    
#    feat_file = '/Volumes/behavgenom_archive$/single_worm/finished/mutants/unc-115(mn481)X@SP1789/food_OP50/XX/30m_wait/anticlockwise/unc-115 (mn481)X on food R_2010_08_19__16_04___3___11_features.hdf5'
#    segworm_feat_file = '/Volumes/behavgenom$/Andre/Laura Grundy/unc-115/mn481/SP1789/on_food/XX/30m_wait/L/tracker_3/2010-08-19___16_04_00/unc-115 (mn481)X on food R_2010_08_19__16_04___3___11_features.mat'
    
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/egl-10(md176)V@MT8504/food_OP50/XX/30m_wait/anticlockwise/egl-10 (md176)V on food R_2010_12_16__15_45___3___7.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/egl-10/md176/MT8504/on_food/XX/30m_wait/L/tracker_3/2010-12-16___15_45_00/egl-10 (md176)V on food R_2010_12_16__15_45___3___7_features.mat'''

#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/sem-4(ga82)I@EW35/food_OP50/XX/30m_wait/clockwise/sem-4 (ga82)I on food L_2010_07_29__15_54___3___11.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/sem-4/ga82/EW35/on_food/XX/30m_wait/R/tracker_3/2010-07-29___15_54_00/sem-4 (ga82)I on food L_2010_07_29__15_54___3___11_features.mat'''
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/unc-105(ok1432)II@RB1316/food_OP50/XX/30m_wait/anticlockwise/unc-105 (ok1432) on food R_2010_07_08__11_03___3___3.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/unc-105/ok1432/RB1316/on_food/XX/30m_wait/L/tracker_3/2010-07-08___11_03_00/unc-105 (ok1432) on food R_2010_07_08__11_03___3___3_features.mat'''

#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/unc-2(ox106)X@EG106/food_OP50/XX/30m_wait/anticlockwise/unc-2 (ox106) on food R_2010_04_14__15_55_26___1___15.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/unc-2/ox106/EG106/on_food/XX/30m_wait/L/tracker_1/2010-04-14___15_55_26/unc-2 (ox106) on food R_2010_04_14__15_55_26___1___15_features.mat'''

#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/WT/N2/food_OP50/XO/30m_wait/anticlockwise/N2 male on food R_2012_02_23__11_59_06___1___2.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/gene_NA/allele_NA/N2/on_food/XO/30m_wait/L/tracker_1/2012-02-23___11_59_06/N2 male on food R_2012_02_23__11_59_06___1___2_features.mat'''
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/egl-12(n602)V@MT1232/food_OP50/XX/30m_wait/clockwise/egl-12 (n602)V on food L_2010_07_09__15_02_19___6___7.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/egl-12/n602/MT1232/on_food/XX/30m_wait/R/tracker_6/2010-07-09___15_02_19/egl-12 (n602)V on food L_2010_07_09__15_02_19___6___7_features.mat'''
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/sma-3(e491)III@CB491/food_OP50/XX/30m_wait/clockwise/sma-3 (e491)III on food L_2011_09_22__16_24_24___7___11.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/sma-3/e491/CB491/on_food/XX/30m_wait/R/tracker_7/2011-09-22___16_24_24/sma-3 (e491)III on food L_2011_09_22__16_24_24___7___11_features.mat'''
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/WT/N2/food_OP50/XX/30m_wait/anticlockwise/N2 on food R_2010_04_13__10_24_52___6___1.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/gene_NA/allele_NA/N2/on_food/XX/30m_wait/L/tracker_6/2010-04-13___10_24_52/N2 on food R_2010_04_13__10_24_52___6___1_features.mat'''
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/flp-7(ok2625)X@RB1990/food_OP50/XX/30m_wait/clockwise/flp-7 (ok2625)X on food L_2010_01_11__11_56_46___6___2.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/flp-7/ok2625/RB1990/on_food/XX/30m_wait/R/tracker_6/2010-01-11___11_56_46/flp-7 (ok2625)X on food L_2010_01_11__11_56_46___6___2_features.mat'''
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/flp-12(ok2409)X@RB1863/food_OP50/XX/30m_wait/anticlockwise/flp-12 (ok2409)X on food R_2010_01_11__12_16_50__2.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/flp-12/ok2409/RB1863/on_food/XX/30m_wait/L/tracker_5/2010-01-11___12_16_50/flp-12 (ok2409)X on food R_2010_01_11__12_16_50__2_features.mat'''
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/C18B2.6(ok2353)X@RB1818/food_OP50/XX/30m_wait/clockwise/C1B2.6 (ok2353) on food L_2010_03_30__15_51_48___8___9.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/C18B2.6/ok2353/RB1818/on_food/XX/30m_wait/R/tracker_8/2010-03-30___15_51_48/C1B2.6 (ok2353) on food L_2010_03_30__15_51_48___8___9_features.mat'''
#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/unc-26(m2)IV@DR2/food_OP50/XX/30m_wait/anticlockwise/unc-26 (m2)IV on food R_2010_04_16__11_58_52___8___6.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/unc-26/m2/DR2/on_food/XX/30m_wait/L/tracker_8/2010-04-16___11_58_52/unc-26 (m2)IV on food R_2010_04_16__11_58_52___8___6_features.mat'''

#    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/osm-9(ky10)IV@CX10/food_OP50/XX/30m_wait/anticlockwise/osm-9 (ky10) on food R_2010_07_08__11_24_27___2___4.hdf5
#/Volumes/behavgenom$/Andre/Laura Grundy/osm-9/ky10/CX10/on_food/XX/30m_wait/L/tracker_2/2010-07-08___11_24_27/osm-9 (ky10) on food R_2010_07_08__11_24_27___2___4_features.mat'''
    dd = '''/Volumes/behavgenom_archive$/single_worm/finished/mutants/unc-17(e245)IV@CB933/food_OP50/XX/30m_wait/clockwise/unc-17 (e245) on food L_2010_04_16__14_27_51___6___10.hdf5
/Volumes/behavgenom$/Andre/Laura Grundy/unc-17/e245/CB933/on_food/XX/30m_wait/R/tracker_6/2010-04-16___14_27_51/unc-17 (e245) on food L_2010_04_16__14_27_51___6___10_features.mat'''

    feat_file, segworm_feat_file = dd.split('\n')
    feat_file = feat_file.replace('.hdf5', '_features.hdf5')
    
    
    feats_reader = FeatsReaderComp(feat_file, segworm_feat_file)
    
    skeletons, skel_segworm = feats_reader.read_skeletons()
    
    
    #%%
    plot_skel_diff(-skeletons, -skel_segworm)
    #%%
    
    
    #%%
if __name__ == '__main__':
    main()
    #main_single()
    pass