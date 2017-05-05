#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  3 11:25:27 2017

@author: ajaver
"""
from scipy.io import loadmat

segworm_feat_file = '/Users/ajaver/OneDrive - Imperial College London/Ev_L4 worms/RawVideos/worm 2/L4_H_18_2016_10_30__15_56_12___features.mat'

dat  = loadmat(segworm_feat_file)


dat['worm'][0,0]['locomotion'][0,0]
'/worm/locomotion/motion/paused/frames/interDistance