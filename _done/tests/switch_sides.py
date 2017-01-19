# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 09:07:56 2016

@author: ajaver
"""

import tables
import json
import numpy as np
from MWTracker.featuresAnalysis.obtainFeaturesHelper import calWormAreaSigned, switchCntSingleWorm


skeletons_file = '/Users/ajaver/Desktop/Videos/single_worm/agar_4/Results/N2 on food R_2010_01_12__10_38_59___1___1_skeletons.hdf5'
#skeletons_file = '/Users/ajaver/Desktop/Videos/single_worm/agar_4/Results/N2 on food L_2010_04_21__10_29_55___8___1_skeletons.hdf5'

with tables.File(skeletons_file, 'r+') as fid:
    exp_info_b = fid.get_node('/experiment_info').read()
    exp_info = json.loads(exp_info_b.decode("utf-8"))
    if not exp_info['ventral_side'] in ['clockwise', 'anticlockwise']:
        raise ValueError('"{}" is not a valid value for '
        'ventral side orientation. Only "clockwise" or "anticlockwise" '
        'are accepted values'.format(exp_info['ventral_side']))

    #maybe it would be faster do not check all the contour orientation but better 
    #play safe than sorry.
    has_skeletons = fid.get_node('/trajectories_data').col('has_skeleton')
    valid_ind = np.where(has_skeletons)[0][0]
    cnt_side1 = fid.get_node('/contour_side1')[valid_ind,:,:]
    cnt_side2 = fid.get_node('/contour_side2')[valid_ind,:,:]
    
    A_sign = calWormAreaSigned(cnt_side1, cnt_side2)
    
    #if not (np.all(A_sign > 0) or np.all(A_sign < 0)):
    #    raise ValueError('There is a problem. All the contours should have the same orientation.')

    #change contours if they do not match the known orientation
    if (exp_info['ventral_side'] == 'clockwise' and A_sign[0] < 0) or \
        (exp_info['ventral_side'] == 'anticlockwise' and A_sign[0] > 0):
        #since here we are changing all the contours, let's just change the name of the datasets
        side1 = fid.get_node('/contour_side1')
        side2 = fid.get_node('/contour_side2')
        
        side1.rename('contour_side1_bkp')
        side2.rename('contour_side1')
        side1.rename('contour_side2')

#switchCntSingleWorm(skeletons_file)