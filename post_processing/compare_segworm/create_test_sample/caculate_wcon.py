# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import glob
import os

from tierpsy.analysis.wcon_export import exportWCON
from tierpsy.analysis.vid_subsample import createSampleVideo

main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3'


feat_files = glob.glob(os.path.join(main_dir, '*_features.hdf5'))
mask_files = [x.replace('_features.hdf5', '.hdf5') for x in feat_files]


#for mask_file in mask_files:
#    createSampleVideo(mask_file)

for feat_file in feat_files:
    exportWCON(feat_file)
