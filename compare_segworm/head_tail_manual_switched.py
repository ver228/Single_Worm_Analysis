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

good_files_str = '''/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-116 (e2310)III on food L_2010_07_29__14_56___3___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/osm-9 (ky10) on food R_2010_06_15__14_57_24___8___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-108 (n501)I on food L_2009_12_10__14_02_38___2___9.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-103 (e1597)II on food R_2010_08_06__15_41_28___8___11.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/flp-25 (gk1016)III on food L_2010_01_12__13_07_15___4___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-6 (n592)X on food L_2010_05_11__14_51_15___7___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-14 (n549)X on food L_2010_07_15__16_20___3___14.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/flp-6 (ok3056)V on food R_2010_01_14__11_35___3___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/gar-2 (ok250)III on food R_2010_07_22__11_23_27___1___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/N2 on food R_2011_05_24__13_03_48___7___6.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/vab-7 (e1562)III on food L_2011_10_13__11_49_40___1___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/flp-25 (gk1016)III on food R_2010_01_12__13_06_48___2___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-6 (n592)X on food R_2010_05_13__15_47___3___13.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/N2 on food L_2010_11_26__16_25_46___6___13.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/flp-16 (ok3085) on food L_2010_01_11__12_35_14___7___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/flr-1 (ut11) on food L_2010_04_09__15_53_02___1___14.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-32 (n155)I  on food l_2010_05_11__16_50_11___7___13.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-1 (n487)V on food R_2010_07_15__11_47_56___1___4.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/daf-5 (e1386)II on food L_2010_07_22__14_46_33__8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/rab-3 (cy250) on food L_2011_08_04__11_10_43___2___3.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/acr-2 (ok1887) on food r_2010_02_19__14_43_43___8___13.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-27 (ok151)II on food R_2010_09_24__12_55___3___6.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-32 (n155)I on food R_2010_05_13__15_03_22___1___11.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-16 (e109) on food L_2009_12_11__12_21___3___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-63 (ok1075) on food L_2010_04_16__12_57_13___8___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-12 (n602)V on food L_2010_07_16__12_05_00___1___6.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/gpa-8 (pk435)V on food L_2010_03_11__10_25_35___8___2.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-79 (e1068)III on food L_2010_04_13__15_39_23___8___14.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-46 (n1127)V on food L_2010_08_06__16_02_11___7___13.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-8 (v488) on food R_2011_09_20__13_33_10___7___7.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/N2 on food L_2010_11_09__15_36_39___1___8.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-60 (e273)V on food L_2010_04_15__13_07_43__9.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/asic-1 (ok415) on food R_2010_06_15__11_26_21___2___3.hdf5'''

partial_files_str = '''/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-116 (e2310)III on food L_2010_07_29__14_56___3___8.hdf5
15401-15415
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-101 (e1265) on food L_2010_09_23__12_37_31___8___6.hdf5
19804-19806, 19819-19830, 19886-19893, 19904-19907, 19921-19931,  19938-19938, 19945-19945, 19985-19986, 20055-20055
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/egl-27 (ok151)II on food L_2010_08_05__14_44_24___2___11.hdf5
14045-14045, 14173-14184, 14226-14226, 14298-14298, 14333-14334, 14344-14344, 14378-14378
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/trp-1 (sy691) on food R_2010_04_21__14_59_17___8___10.hdf5
12231-12231, 12242-12243, 12250-12273, 12285-12285, 12295-12299, 12306-12306, 12331-12346, 12421-12457, 12464-12469, 12479-12480, 12664-12664, 12677-12701, 12830-12888, 12895-12923, 12930-12931, 
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-104 (e1265)III on food R_2011_10_18__15_39___4___10.hdf5
2608-3747, 3755-5270
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-105 (ok1432) on food L_2010_07_06__11_44_23___2___6.hdf5
1812-1819, 1826-1832
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/acr-15 (ok1214)X on food L_2010_02_24__15_45_04___8___14.hdf5
250-411, 419-424, 700-700, 793-799, 808-811, 1012-1018, 1032-1032, 18761-18814
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-101 (e1265) on food R_2010_09_24__11_35___3___2.hdf5
810-810, 18597-18597, 18608-18608, 23978-23982, 23988-23993
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-38 (e264)I on food L_2010_08_19__12_34_15___1___6.hdf5
7480-7582, 7590-7590, 7596-7596, 7603-7607, 7617-7643, 7652-7652, 7663-7722, 7733-7736, 7806-7963
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-76 (e911)V on food L_2010_04_14__11_22_30___8___5.hdf5
12445-12445, 12455-12459, 12475-12316, 12242-13344, 13354-13362, 13368-15598, 18411-18411, 18510-18510
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-76 (e911)V on food R_2010_04_13__11_06_24___4___3.hdf5
3240-3249, 3258-3265, 3286-3294, 3328-3332, 18547-18547, 18585-18589
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-101 (e1265) on food L_2010_09_17__16_04_15___1___8.hdf5
20530-20530, 20536-23004 '''

bad_track_files_str = '''/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-32 (e189) on food L_2009_12_09__15_57_51___2___13.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/acr-21 (ok1314)III on food L_2010_02_24__14_45_13__11.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-17 (e245) on food R_2010_04_16__14_27_23___2___8.hdf5'''

wrong_files_str = '''/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-1 (e1598)X on food R_2010_04_14__11_58_21___2___7.hdf5
/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-18 (e81)X on food R_2011_08_09__12_33_45___8___7.hdf5'''

partial_wrong_files_str ='''/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-18 (e81)X on food R_2011_08_24__10_24_18__2.hdf5
17709-17735, 17743-17758, 17772-17772, 17782-17788, 17795-17795, 17801-17801'''

good_files = good_files_str.split('\n')
bad_track_files = bad_track_files_str.split('\n')
wrong_files = wrong_files_str.split('\n')

def read_partial_files(f_str):
    dd = f_str.split('\n')
    index_dict = {}
    fnames = []
    for ii in range(0, len(dd),2 ):
        fname = dd[ii]
        indexes_str = dd[ii+1]
        indexes = [tuple(map(int, x.split('-'))) for x in indexes_str.split(', ') if x]
        index_dict[fname] = indexes
        fnames.append(fname)
    return fnames, index_dict

partial_files, bad_index_dict = read_partial_files(partial_files_str)
wrong_partial_files, good_index_dict = read_partial_files(partial_wrong_files_str)


files = bad_track_files + partial_files + wrong_partial_files+ wrong_files + good_files

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
        for bad_index in bad_indexes:
            bad_timestamp = timestamp_raw[bad_index[0]:bad_index[1]+1]
            bad_vec[bad_timestamp] = True
        #make false the once without skeletons to avoid double counting
        bad_vec[np.isnan(skeletons[:,0,0])] = False
        
    elif masked_image_file in good_index_dict:
        good_indexes = good_index_dict[masked_image_file]
        bad_vec = ~np.isnan(skeletons[:,0,0])
        for good_index in good_indexes:
            good_timestamp = timestamp_raw[good_index[0]:good_index[1]+1]
            bad_vec[good_timestamp] = False
    elif masked_image_file in wrong_files:
        bad_vec = ~np.isnan(skeletons[:,0,0])
    else:
        tot_bad_skel = 0
    tot_bad_skel = sum(bad_vec)
    
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
#%%
main_dir = '/Users/ajaver/Desktop/Videos/single_worm/switched_sample/'
all_files = [os.path.join(main_dir, x) for x in os.listdir(main_dir) if not '_features' in x and not '_skeletons' in x and not x.startswith('.')]
print([x for x in all_files if x not in files])
#%%
bad_old = [(x+y)/z for x,y,z in zip(new1old0, new0old0, tot_common)]
bad_new = [(x+y)/z for x,y,z in zip(new0old1, new0old0, tot_common)]
plt.figure()
plt.plot(bad_old, 'sr')
plt.plot(bad_new, 'og')

