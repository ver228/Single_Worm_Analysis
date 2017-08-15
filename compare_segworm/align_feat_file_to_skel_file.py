#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 17:41:09 2017

@author: ajaver
"""
import os
import tables
import numpy as np
from tierpsy.helper.params import read_microns_per_pixel
from tierpsy.analysis.stage_aligment.alignStageMotion import isGoodStageAligment, _h_get_stage_inv


mask_file = '/Volumes/behavgenom_archive$/single_worm/finished/mutants/cat-2(e1112)II@CB1112/food_OP50/XX/30m_wait/anticlockwise/cat-2 (e112) on food R_2009_10_08__12_21_25___2___1.hdf5'
skeletons_file = mask_file.replace('.hdf5', '_skeletons.hdf5')

#finally if the stage was aligned correctly add the information into the mask file    
if os.path.exists(mask_file) and isGoodStageAligment(skeletons_file):
    microns_per_pixel = read_microns_per_pixel(mask_file)
    with tables.File(mask_file, 'r+') as fid:
        n_frames = fid.get_node('/mask').shape[0]
        timestamp_c = fid.get_node('/timestamp/raw')[:]
        timestamp = np.arange(np.min(timestamp_c), np.max(timestamp_c)+1)
        stage_vec_inv, ind_ff = _h_get_stage_inv(skeletons_file, timestamp)
        stage_vec_pix = stage_vec_inv[ind_ff]/microns_per_pixel
        if '/stage_position_pix' in fid: 
            fid.remove_node('/', 'stage_position_pix')
        fid.create_array('/', 'stage_position_pix', obj=stage_vec_pix)