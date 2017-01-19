# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 15:16:47 2016

@author: ajaver
"""
import os
import h5py

flists = '/Volumes/behavgenom$/Kezhi/DataSet/AllFiles/MaskedVideos/files2process.txt'
results_dir = '/Volumes/behavgenom$/Kezhi/DataSet/AllFiles/OutSource_files/All_Label/Ave'

files2check = [
'655 JUU394 on food L_2011_03_09__16_33___3___12(3)',
'N2 L4 on food L_2010_06_24__11_15_35___1___4(0)',
'N2 L4 on food R_2010_06_24__12_28_04___1___7(0)',
'N2 L4 on food _2010_06_24__11_17_15___4___4(6)',
'N2 L4 on food_2010_02_11__11_47_29___1___5(12)',
'N2 pmyo3-GCaMP3-SL2-RFP @ 50 on food L_2010_06_16__11_39_41___1___5(0)',
'N2 pmyo3-GCaMP3-SL2-RFP @ 75 on food L_2010_06_16__12_01_34___1___6(6)',
'N2 unc-47-GCaMP3-SL2-RFP on food L_2010_06_16__10_56_41___1___3(0)',
'T1 N2-30MINON MORPHINE ON NALOXONE_2010_03_18__20_05_49___1___6(12)',
'T1 N2-30MINON MORPHINE ON NALOXONE_2010_03_18__21_39_22___1___8(12)',
'T1 N2-NO TRWEATMENT NO DRUGS_2010_03_19__00_09_00___1___11(12)',
'T1 N2-ON MORPHINE ON NALOXONE_2010_03_18__19_43_15___1___5(12)',
'T1_N2_NALOXONE10X_4DAYS_OFF NALOXONE_2010_03_09__21_02_18___1___2(12)',
'cat-2 L4 on food L_2010_06_24__10_31_40___1___2(0)',
'cat-2 L4 on food R_2010_06_24__11_39_11___1___5(0)',
'dop-3 L4 on food L_2010_06_24__10_56_27___1___3(0)',
'lite-1 pmyo3-GCaMP3-SL2-RFP @ 30 on food L_2010_06_16__13_05_52___1___9(0)',
'lite-1 pmyo3-GCaMP3-SL2-RFP @ 75 on food L_2010_06_16__12_19_42___1___7(0)',
'mec-10 (e1515) off food x_2009_10_28__17_12_13__3(2)',
'mec-7 (e1506) off food x_2009_10_28__17_29_02__2(1)',
'pmyo-3-GCaMP3-mRuby R_2009_12_12__16_26_27__3(14)',
'scd2b-morphine treated assayed on naloxone_2010_04_29__20_20_36___1___14(11)',
]

with open(flists, 'r') as fid:
    files = [x for x in fid.read().split('\n') if x]
    
for ii, fname in enumerate(files):
    fname = fname.replace('behavgenom$-1/', 'behavgenom$/')
    base_name = os.path.splitext(os.path.basename(fname))[0]
    if not os.path.exists(fname):
        continue
    
    if not base_name in files2check:
        continue
    
    with h5py.File(fname, 'r') as fid:
        mask_size = fid['/mask'].shape[0]
        
    
    skeletons_file = os.path.join(results_dir, base_name + '_skeletons.hdf5')
    with h5py.File(skeletons_file, 'r') as fid:
        skel_size = fid['/skeleton'].shape[0]
    
    #if mask_size < skel_size:
    print(ii, mask_size, skel_size)