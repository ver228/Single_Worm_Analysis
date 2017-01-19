# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 22:01:59 2016

@author: ajaver
"""

import h5py
import tables
import os
import numpy as np
import matplotlib.pylab as plt
from scipy.io import loadmat
import glob
import os
import pandas as pd

from MWTracker.featuresAnalysis.obtainFeaturesHelper import WormFromTable
from MWTracker.featuresAnalysis.obtainFeatures import getMicronsPerPixel, getFPS

good_files_str = '''/Users/ajaver/Desktop/Videos/single_worm/global_sample/snf-1 (ok790)I on food L_2009_11_17__12_22_54___7___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food L_2011_02_17__12_51_07___7___7.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-44 (n1080)II on food R_2010_08_19__15_08_14___7___10.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/mec-14 (v55) on food R_2010_10_14__14_59___3___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food R_2011_05_24__12_20___3___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-3 (e151)X on food L_2011_10_21__11_57___3___6.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food R_2011_06_30__12_40___3___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/pgn-66 (ok1507) on food L_2010_04_22__09_49_27___4___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food L_2009_11_18__10_11_48___2___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/972 JU345 on food R_2011_03_28__15_44___3___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-89 (e140)I on food R_2010_04_09__14_56_17___7___11.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ins-28 (ok2722)I on food R_2011_05_12__10_43_41___7___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/flp-11 (tm2706)X on food R_2010_01_14__13_13_06___8___9.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/CIID2.2 (gk9)IV on food L_2011_08_04__10_33_17__1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/trp-2 (sy691) on food R_2010_03_19__11_33___3___7.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-42 (e270)I on food R_2010_08_06__11_17_40__2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-6 (n592)X on food L_2010_05_11__14_51_15___7___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food R_2010_07_16__10_27_41__1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-60 (e273)V on food R_2010_04_14__12_38_26___4___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/flp-20 (ok2964)X on food R_2011_06_30__13_03_29___7___9.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ins-15 (ok3444)II on food L_2011_06_07__10_42_58___7___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-32 (n155)I on food L_2010_05_11__16_48_03___2___13.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/T28F2.7 (ok2657) on food R_2010_03_30__12_27_54___4___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ins-25 (ok2773)I on food L_2011_05_24__15_20_12___2___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/C38D9.2 (ok1853) on food R_2011_09_22__15_39___3___9.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-8 (n488)V on food R_2010_05_11__12_26_00___7___5.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 male on food R_2012_02_22__10_58_13___4___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-7 (cb5) on food R_2010_09_10__11_44_55___2___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/nlp-14 (tm1880)X on food L_2010_03_17__10_53_10___1___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/gpa-10 (pk362)V on food L_2010_02_25__10_43_09___1___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food L_2011_03_30__15_12_28___7___7.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/nlp-1 (ok1469)X on food R_2010_03_17__12_55_03___1___9.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/gon-2 (9362) on food R_2010_04_22__10_49_08___4___5.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/bas-1 (ad446) on food R_2009_12_17__15_53_54___7___12.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-86 (e1416)III on food R_2010_09_24__11_54_11___1___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/814 JU393 on food R_2011_04_13__11_22_12___8___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-7 (cb5) on food R_2010_09_09__10_26_33___4___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-105 (ok1432) on food R_2010_04_16__10_37___3___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/nca-1 nca-2 on food L_2011_10_06__10_55_29__1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ins-27 (ok2474)I on food L_2011_06_09__10_48_33___2___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/snf-9 (ok957)IV on food R_2009_11_17__15_28_18___7___7.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/acr-7 (tm863)II on food L_2010_02_19__11_45_15__8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-20 (mu39)IV on food R_2010_07_15__12_30_59___8___6.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food L_2012_02_09__11_16___4___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food L_2010_01_20__09_53_36___4___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/T28F2.7 (ok2657) on food L_2010_03_31__11_14_06___2___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/npr-11 (ok594)X on food R_2010_01_28__11_15_57__3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/sng-1 (ok234)X on food R_2011_09_20__15_19___3___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-86 (e1416)III on food R_2010_09_24__11_58_07___7___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-11 (n587)V on food R_2010_05_13__10_54_38___4___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food R_2010_03_12__09_53___3___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ocr-4 (vs137); ocr-2 (9447); ocr-1 (ok134) on food L_2010_07_08__10_46_10___8___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/mec-12 (u76) on food L_2010_10_28__15_07___3___10.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/gpa-15 (pk477)I on food R_2010_03_05__11_54_26___4___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/nlp-17 (ok3461)IV on food R_2010_03_12__10_34_51___7___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ser-4 (ok512) on food R_2009_12_17__12_08_09__5.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food L_2010_07_22__11_06_30___8___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/mec-10 (e1515) on food L_2010_10_28__11_58_35___7___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-98 (st85)I on food L_2010_04_15__11_09_48___4___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/mec-14 (v55) on food L_2010_11_11__11_50_26__3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-34 on food R_2010_09_17__12_35___3___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/gld-1 (op236)I on food L_2012_03_08__15_49_16___7___9.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food R_2011_04_14__11_30_56___6___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/764 ED3049 on food L_2011_03_28__15_46_59__7.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-7 (cb5) on food R_2010_08_19__11_20_10___8___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/nca-1 nca-2 on food L_2011_10_06__10_55_29__1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food L_2010_04_15__10_08___3___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/gly-2 (gk204)I on food L_2011_08_25__13_03_21___8___6.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-75 (e950)I on food L_2010_08_20__12_36___3___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-17 (e1313)X on food L_2010_07_20__15_33_27___1___11.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/dpy-20 (e1282)IV on food L_2011_08_04__11_50___3___5.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/acr-2 (ok1887) on food L_2010_02_23__10_55___3___7.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/flp-25 (gk1016)III on food R_2010_01_11__12_53_41___2___5.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food R_2011_09_22__12_31___4___5.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/trp-4 (sy695) on food L_2010_04_22__10_28___3___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food L_2010_01_20__09_54_23___8___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ser-2 (pk1357) on food L_2009_12_15__14_45_23___4___9.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/532 CB4853 on food L_2011_03_09__12_00_26___8___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food R_2011_03_29__15_55_07___6___12.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ins-35 (ok3297)V on food R_2011_05_12__10_40___3___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-55 (e402)I on food R_2011_11_04__10_10_15__2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/507 ED3054 on food L_2011_02_17__16_45_44__11.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food R_2012_02_09__10_28___4___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/mec-12 (u76) on food R_2010_10_28__11_17_48__2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-37 (n742)II on food L_2010_08_05__11_45_56___4___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/npr-12 (tm1498)IV on food R_2010_01_26__15_56_07___1___11.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/tag-24 (ok371)X  on food  R_2010_01_22__15_04_50___8___11.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-8 (e15)I on food R_2011_10_21__10_18___4___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/acr-3 (ok2049)X on food R_2010_02_24__11_03_47___2___6.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ocr-4 (vs137) on food R_2010_04_21__15_20_27__12.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-13 (n483)X on food L_2010_07_16__11_03_30___1___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food R_2010_03_04__09_03_02___8___1.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/972 JU345 ON FOOD l_2011_03_29__11_44_56___6___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ins-3 (ok2488)II on food L_2011_05_17__11_55_03___8___4.hdf5'''

partial_files_str = '''/Users/ajaver/Desktop/Videos/single_worm/global_sample/egl-30 (ep271gf) on food R_2010_03_05__12_56_35___7___11.hdf5
1-9
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-43 (e755)IV on food L_2010_08_05__14_24___3___9.hdf5
2981-2990, 2996-3000, 11541-11599, 11829-11868, 13238-13239, 14384-14412,  14563-14564
/Users/ajaver/Desktop/Videos/single_worm/global_sample/acr-19 (ad1674) on food L_2010_02_23__11_34_38___7___8.hdf5
6465-6479
/Users/ajaver/Desktop/Videos/single_worm/global_sample/N2 on food L_2010_11_04__10_34_29___1___1.hdf5
14055-14055
/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-115 (mn481)Xon food L_2010_08_19__16_06_40___8___12.hdf5
11938-11957
/Users/ajaver/Desktop/Videos/single_worm/global_sample/ocr-3 (a1537) on food L_2010_04_22__11_50_03__8.hdf5
5142-5146
/Users/ajaver/Desktop/Videos/single_worm/global_sample/flp-16 (ok3085) on food R_2010_01_14__12_36_45__7.hdf5
4122-4151, 4158-4175, 4185-4185, 4216-4221, 4239-4239, 4259-4275, 4283-4286, 4298-4298, 4332-4332, 4345-4351, 4357-4359, 4369-4370, 5552-5552, 5753-5758, 5765-5771, 5870-5881, 5891-5902, 5916-6033, 6079-6088, 6113-6153, 6206-6221, 10779-10779, 10792-10804, 10812-10860, 10986-11007'''

bad_files = ['/Users/ajaver/Desktop/Videos/single_worm/global_sample/unc-32 (e189) on food R_2009_12_11__16_54_38___7___14.hdf5']
good_files = good_files_str.split('\n')

dd = partial_files_str.split('\n')
bad_index_dict = {}
partial_files = []
for ii in range(0, len(dd),2 ):
    fname = dd[ii]
    bad_indexes_str = dd[ii+1]
    bad_indexes = [tuple(map(int, x.split('-'))) for x in bad_indexes_str.split(', ')]
    bad_index_dict[fname] = bad_indexes
    partial_files.append(fname)

files = bad_files + partial_files + good_files

all_dat = []
for mask_id, masked_image_file in enumerate(files):
    
    dd = masked_image_file[:-5]
    segworm_feat_file = dd + '_features.mat'
    skeletons_file = dd + '_skeletons.hdf5'
    features_file = dd + '_features.hdf5'
    
    if not os.path.exists(features_file):
        continue
    
    print(mask_id, masked_image_file)
    
    #read data from the new sekeltons
    skeletons = np.zeros(0) #just to be sure i am not using a skeleton for another file
    with tables.File(features_file, 'r') as fid:
        #if '/features_means' in fid and \
        #fid.get_node('/features_means').attrs['has_finished'] and \
        #fid.get_node('/features_timeseries').shape[0]>0:
        skeletons = fid.get_node('/skeletons')[:]
        if skeletons.size > 0:
            frame_range = fid.get_node('/features_events/worm_1')._v_attrs['frame_range']
            #pad the beginign with np.nan to have the same reference as segworm (time 0)
            skeletons = np.pad(skeletons, [(frame_range[0],0), (0,0), (0,0)], 
                       'constant', constant_values=np.nan)
        #else:
        #     continue
    
    with tables.File(skeletons_file, 'r') as fid:
        timestamp_raw = fid.get_node('/timestamp/raw')[:].astype(np.int)
    
    #read data from the old skeletons
    fvars = loadmat(segworm_feat_file, struct_as_record=False, squeeze_me=True)
    micronsPerPixels_x = fvars['info'].video.resolution.micronsPerPixels.x
    micronsPerPixels_y = fvars['info'].video.resolution.micronsPerPixels.y
    
    segworm_x = -fvars['worm'].posture.skeleton.x.T
    segworm_y = -fvars['worm'].posture.skeleton.y.T
    segworm = np.stack((segworm_x,segworm_y), axis=2)
    
    #get the total number of skeletons
    tot_skel = np.sum(~np.isnan(skeletons[:,0,0]))
    tot_seg = np.sum(~np.isnan(segworm[:,0,0]))
    #correct in case the data has different size shape
    max_n_skel = min(segworm.shape[0], skeletons.shape[0])
    skeletons = skeletons[:max_n_skel]
    segworm = segworm[:max_n_skel]
    
    #shift the skeletons coordinate system to one that diminushes the errors the most.
    seg_shift = np.nanmedian(skeletons-segworm, axis = (0,1))
    segworm += seg_shift
    
    #print('S', seg_shift)
    #%%
    R_ori = np.sum(np.sqrt(np.sum((skeletons-segworm)**2, axis=2)), axis=1)
    R_inv = np.sum(np.sqrt(np.sum((skeletons[:,::-1,:]-segworm)**2, axis=2)), axis=1)
    
    bad_ind = np.isnan(R_ori)
    ht_mismatch = np.argmin((R_ori, R_inv), axis =0)
    ht_mismatch[bad_ind] = 0
    #%%
    bad_vec = np.zeros(skeletons.shape[0], np.bool)
    if masked_image_file in bad_index_dict:
        bad_indexes = bad_index_dict[masked_image_file]
        tot_bad_skel = sum(y-x+1 for x,y in bad_indexes)
        
        for bad_index in bad_indexes:
            bad_timestamp = timestamp_raw[bad_index[0]:bad_index[1]+1]
            bad_vec[bad_timestamp] = True
            tot_bad = np.sum(bad_vec)
    else:
        tot_bad_skel = 0
    
    good_ind = ~bad_ind
    tot_common = np.sum(good_ind)
    
    #%%
    new1old0 = np.sum(ht_mismatch & ~bad_vec & good_ind)
    new0old1 = np.sum(ht_mismatch & bad_vec & good_ind)
    new1old1 = np.sum(~ht_mismatch & ~bad_vec & good_ind)
    new0old0 = np.sum(~ht_mismatch & bad_vec & good_ind)
    #%%
    all_dat.append((tot_skel, tot_seg, tot_bad_skel, tot_common, new1old0, new0old1, new1old1, new0old0))
    #%%
    if False:
        w_xlim = w_ylim = (-10, skeletons.shape[0]+10)
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(skeletons[:,1,1], 'b')
        plt.plot(segworm[:,1,1], 'r')
        plt.xlim(w_ylim)
        plt.ylabel('Y coord')
        
        plt.subplot(2,1,2)
        plt.plot(skeletons[:,1,0], 'b')
        plt.plot(segworm[:,1,0], 'r')
        plt.xlim(w_xlim)
        plt.ylabel('X coord')
        plt.xlabel('Frame Number')
#%%
tot_skel, tot_seg, tot_bad_skel, tot_common, new1old0, new0old1, new1old1, new0old0 = zip(*all_dat)
only_seg = tuple(x-y for x,y in zip(tot_seg, tot_common))
only_skel = tuple(x-y for x,y in zip(tot_skel, tot_common))
#%%

#%%
tot_skels = sum(tot_skel)
tot_segs = sum(tot_seg)
tot_commons = sum(tot_common)

tot_union = tot_skels + tot_segs - tot_commons

frac_only_seg = (tot_skels - tot_commons) / tot_union
frac_only_skel = (tot_segs - tot_commons) / tot_union
frac_mutual =  tot_commons / tot_union
#%%
frac_skel_bad = sum(tot_bad_skel)/tot_skels
#%%
skel_bad_common =1-(sum(new1old0) + sum(new1old1))/tot_commons
seg_bad_common = 1-(sum(new0old1) + sum(new1old1))/tot_commons
