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
import pymysql

import sys
sys.path.append('../../compare_segworm')
from read_feats import FeatsReaderComp

good_basenames = ['snf-1 (ok790)I on food L_2009_11_17__12_22_54___7___2',
 'N2 on food L_2011_02_17__12_51_07___7___7',
 'egl-44 (n1080)II on food R_2010_08_19__15_08_14___7___10',
 'mec-14 (v55) on food R_2010_10_14__14_59___3___1',
 'N2 on food R_2011_05_24__12_20___3___4',
 'unc-3 (e151)X on food L_2011_10_21__11_57___3___6',
 'N2 on food R_2011_06_30__12_40___3___8',
 'pgn-66 (ok1507) on food L_2010_04_22__09_49_27___4___2',
 'N2 on food L_2009_11_18__10_11_48___2___1',
 '972 JU345 on food R_2011_03_28__15_44___3___8',
 'unc-89 (e140)I on food R_2010_04_09__14_56_17___7___11',
 'ins-28 (ok2722)I on food R_2011_05_12__10_43_41___7___1',
 'flp-11 (tm2706)X on food R_2010_01_14__13_13_06___8___9',
 'CIID2.2 (gk9)IV on food L_2011_08_04__10_33_17__1',
 'trp-2 (sy691) on food R_2010_03_19__11_33___3___7',
 'unc-42 (e270)I on food R_2010_08_06__11_17_40__2',
 'egl-6 (n592)X on food L_2010_05_11__14_51_15___7___8',
 'N2 on food R_2010_07_16__10_27_41__1',
 'unc-60 (e273)V on food R_2010_04_14__12_38_26___4___8',
 'flp-20 (ok2964)X on food R_2011_06_30__13_03_29___7___9',
 'ins-15 (ok3444)II on food L_2011_06_07__10_42_58___7___1',
 'egl-32 (n155)I on food L_2010_05_11__16_48_03___2___13',
 'T28F2.7 (ok2657) on food R_2010_03_30__12_27_54___4___4',
 'ins-25 (ok2773)I on food L_2011_05_24__15_20_12___2___8',
 'C38D9.2 (ok1853) on food R_2011_09_22__15_39___3___9',
 'egl-8 (n488)V on food R_2010_05_11__12_26_00___7___5',
 'N2 male on food R_2012_02_22__10_58_13___4___3',
 'unc-7 (cb5) on food R_2010_09_10__11_44_55___2___2',
 'nlp-14 (tm1880)X on food L_2010_03_17__10_53_10___1___4',
 'gpa-10 (pk362)V on food L_2010_02_25__10_43_09___1___4',
 'N2 on food L_2011_03_30__15_12_28___7___7',
 'nlp-1 (ok1469)X on food R_2010_03_17__12_55_03___1___9',
 'gon-2 (9362) on food R_2010_04_22__10_49_08___4___5',
 'bas-1 (ad446) on food R_2009_12_17__15_53_54___7___12',
 'unc-86 (e1416)III on food R_2010_09_24__11_54_11___1___3',
 '814 JU393 on food R_2011_04_13__11_22_12___8___3',
 'unc-7 (cb5) on food R_2010_09_09__10_26_33___4___2',
 'unc-105 (ok1432) on food R_2010_04_16__10_37___3___2',
 'nca-1 nca-2 on food L_2011_10_06__10_55_29__1',
 'ins-27 (ok2474)I on food L_2011_06_09__10_48_33___2___2',
 'snf-9 (ok957)IV on food R_2009_11_17__15_28_18___7___7',
 'acr-7 (tm863)II on food L_2010_02_19__11_45_15__8',
 'egl-20 (mu39)IV on food R_2010_07_15__12_30_59___8___6',
 'N2 on food L_2012_02_09__11_16___4___3',
 'N2 on food L_2010_01_20__09_53_36___4___1',
 'T28F2.7 (ok2657) on food L_2010_03_31__11_14_06___2___2',
 'npr-11 (ok594)X on food R_2010_01_28__11_15_57__3',
 'sng-1 (ok234)X on food R_2011_09_20__15_19___3___8',
 'unc-86 (e1416)III on food R_2010_09_24__11_58_07___7___3',
 'egl-11 (n587)V on food R_2010_05_13__10_54_38___4___3',
 'N2 on food R_2010_03_12__09_53___3___1',
 'ocr-4 (vs137); ocr-2 (9447); ocr-1 (ok134) on food L_2010_07_08__10_46_10___8___2',
 'mec-12 (u76) on food L_2010_10_28__15_07___3___10',
 'gpa-15 (pk477)I on food R_2010_03_05__11_54_26___4___8',
 'nlp-17 (ok3461)IV on food R_2010_03_12__10_34_51___7___3',
 'ser-4 (ok512) on food R_2009_12_17__12_08_09__5',
 'N2 on food L_2010_07_22__11_06_30___8___1',
 'mec-10 (e1515) on food L_2010_10_28__11_58_35___7___4',
 'unc-98 (st85)I on food L_2010_04_15__11_09_48___4___4',
 'mec-14 (v55) on food L_2010_11_11__11_50_26__3',
 'unc-34 on food R_2010_09_17__12_35___3___4',
 'gld-1 (op236)I on food L_2012_03_08__15_49_16___7___9',
 'N2 on food R_2011_04_14__11_30_56___6___1',
 '764 ED3049 on food L_2011_03_28__15_46_59__7',
 'unc-7 (cb5) on food R_2010_08_19__11_20_10___8___3',
 'nca-1 nca-2 on food L_2011_10_06__10_55_29__1',
 'N2 on food L_2010_04_15__10_08___3___1',
 'gly-2 (gk204)I on food L_2011_08_25__13_03_21___8___6',
 'unc-75 (e950)I on food L_2010_08_20__12_36___3___8',
 'egl-17 (e1313)X on food L_2010_07_20__15_33_27___1___11',
 'dpy-20 (e1282)IV on food L_2011_08_04__11_50___3___5',
 'acr-2 (ok1887) on food L_2010_02_23__10_55___3___7',
 'flp-25 (gk1016)III on food R_2010_01_11__12_53_41___2___5',
 'N2 on food R_2011_09_22__12_31___4___5',
 'trp-4 (sy695) on food L_2010_04_22__10_28___3___4',
 'N2 on food L_2010_01_20__09_54_23___8___1',
 'ser-2 (pk1357) on food L_2009_12_15__14_45_23___4___9',
 '532 CB4853 on food L_2011_03_09__12_00_26___8___3',
 'N2 on food R_2011_03_29__15_55_07___6___12',
 'ins-35 (ok3297)V on food R_2011_05_12__10_40___3___1',
 'unc-55 (e402)I on food R_2011_11_04__10_10_15__2',
 '507 ED3054 on food L_2011_02_17__16_45_44__11',
 'N2 on food R_2012_02_09__10_28___4___1',
 'mec-12 (u76) on food R_2010_10_28__11_17_48__2',
 'egl-37 (n742)II on food L_2010_08_05__11_45_56___4___4',
 'npr-12 (tm1498)IV on food R_2010_01_26__15_56_07___1___11',
 'tag-24 (ok371)X  on food  R_2010_01_22__15_04_50___8___11',
 'unc-8 (e15)I on food R_2011_10_21__10_18___4___1',
 'acr-3 (ok2049)X on food R_2010_02_24__11_03_47___2___6',
 'ocr-4 (vs137) on food R_2010_04_21__15_20_27__12',
 'egl-13 (n483)X on food L_2010_07_16__11_03_30___1___3',
 'N2 on food R_2010_03_04__09_03_02___8___1',
 '972 JU345 ON FOOD l_2011_03_29__11_44_56___6___3',
 'ins-3 (ok2488)II on food L_2011_05_17__11_55_03___8___4']

bad_basenames = ['unc-32 (e189) on food R_2009_12_11__16_54_38___7___14.hdf5']
#%%

partial_basenames = {'N2 on food L_2010_11_04__10_34_29___1___1': [(14055, 14055)],
 'acr-19 (ad1674) on food L_2010_02_23__11_34_38___7___8': [(6465, 6479)],
 'egl-30 (ep271gf) on food R_2010_03_05__12_56_35___7___11': [(1, 9)],
 'flp-16 (ok3085) on food R_2010_01_14__12_36_45__7': [(4122, 4151),
  (4158, 4175),
  (4185, 4185),
  (4216, 4221),
  (4239, 4239),
  (4259, 4275),
  (4283, 4286),
  (4298, 4298),
  (4332, 4332),
  (4345, 4351),
  (4357, 4359),
  (4369, 4370),
  (5552, 5552),
  (5753, 5758),
  (5765, 5771),
  (5870, 5881),
  (5891, 5902),
  (5916, 6033),
  (6079, 6088),
  (6113, 6153),
  (6206, 6221),
  (10779, 10779),
  (10792, 10804),
  (10812, 10860),
  (10986, 11007)],
 'ocr-3 (a1537) on food L_2010_04_22__11_50_03__8': [(5142, 5146)],
 'unc-115 (mn481)Xon food L_2010_08_19__16_06_40___8___12': [(11938, 11957)],
 'unc-43 (e755)IV on food L_2010_08_05__14_24___3___9': [(2981, 2990),
  (2996, 3000),
  (11541, 11599),
  (11829, 11868),
  (13238, 13239),
  (14384, 14412),
  (14563, 14564)]}
#%%
def get_file_names(bns):
    bns2print = ','.join(['"{}"'.format(x) for x in bns])
    
    conn = pymysql.connect(host='localhost', db='single_worm_db')
    cur = conn.cursor()
    
    sql = '''
    SELECT base_name, CONCAT(results_dir, '/', base_name, '_features.hdf5') AS tierpsy_file, segworm_file
    FROM experiments_valid AS e
    JOIN segworm_info AS s ON e.id = s.experiment_id
    WHERE base_name in ({});
    '''.format(bns2print)
    cur.execute(sql)
    valid_exps = cur.fetchall()
    return valid_exps
 

all_basenames = good_basenames + bad_basenames + list(partial_basenames.keys())

all_filenames = get_file_names(all_basenames)
#for mask_file in all_filenames:
#    skel_file = mask_file.replace('.hdf5', '_skeletons.hdf5')
#    with pd.HDFStore(skel_file, 'r') as fid:
#        trajectories_data = fid['/trajectories_data']
 


all_dat = []
for mask_id, (base_name, tierpsy_file, segworm_file) in enumerate(all_filenames):
    
    
    feats_reader = FeatsReaderComp(tierpsy_file, segworm_file)
    skeletons, skel_segworm = feats_reader.read_skeletons()
    
    tot_skel = np.sum(~np.isnan(skeletons[:, 0, 0]))
    tot_seg = np.sum(~np.isnan(skel_segworm[:, 0, 0]))
    
    
    max_n_skel = min(skeletons.shape[0], skel_segworm.shape[0])
    skeletons = skeletons[:max_n_skel]
    skel_segworm = skel_segworm[:max_n_skel]
    
    R_ori = np.sum(np.sqrt(np.sum((skeletons-skel_segworm)**2, axis=2)), axis=1)
    R_inv = np.sum(np.sqrt(np.sum((skeletons[:,::-1,:]-skel_segworm)**2, axis=2)), axis=1)
    
    
    ht_mismatch = np.argmin((R_ori, R_inv), axis =0)
    
    
    #%%
    bad_vec = np.zeros(skeletons.shape[0], np.bool)
    if base_name in partial_basenames:
        bad_indexes = partial_basenames[base_name]
        tot_bad_skel = sum(y-x+1 for x,y in bad_indexes)
        
        for bad_index in bad_indexes:
            bad_vec[bad_index[0]:bad_index[1]+1] = True
            tot_bad = np.sum(bad_vec)
    else:
        tot_bad_skel = 0
    
    good_ind = ~np.isnan(R_ori)
    tot_common = np.sum(good_ind)
    
    #%%
    new1old0 = np.sum(ht_mismatch & ~bad_vec & good_ind)
    new0old1 = np.sum(ht_mismatch & bad_vec & good_ind)
    new1old1 = np.sum(~ht_mismatch & ~bad_vec & good_ind)
    new0old0 = np.sum(~ht_mismatch & bad_vec & good_ind)
    #%%
    all_dat.append((tot_skel, tot_seg, tot_bad_skel, tot_common, new1old0, new0old1, new1old1, new0old0))
    
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
