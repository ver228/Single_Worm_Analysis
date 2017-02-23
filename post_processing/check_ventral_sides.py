#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 13:47:03 2017

@author: ajaver
"""


#ff = "/Volumes/behavgenom_archive$/single_worm/MaskedVideos/nas207-1/experimentBackup/from pc220-7/!worm_videos/copied from pc207-16/Andre/24-03-11/N2 on food R_2011_03_29__16_57_44___1___16.hdf5"
ff = '/Volumes/behavgenom_archive$/single_worm/MaskedVideos/nas207-1/experimentBackup/from pc207-7/!worm_videos/copied_from_pc207-13/Andre/29-03-11/N2 on food R_2011_03_29__16_57_44___1___16.hdf5'

import tables

with tables.File(ff, 'r') as fid:
    print(fid.get_node('/mask').shape)