#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 15:44:36 2017

@author: ajaver
"""
import tables
import numpy as np
import matplotlib.pylab as plt
import pandas as pd

feats_conv = pd.read_csv('../../conversion_table.csv').dropna()
FEATS_MAT_MAP = {row['feat_name_tierpsy']:row['feat_name_segworm'] for ii, row in feats_conv.iterrows()}
FEATS_OW_MAP = {row['feat_name_tierpsy']:row['feat_name_openworm'] for ii, row in feats_conv.iterrows()}

def read_feats_segworm(segworm_feat_file):
    with tables.File(segworm_feat_file, 'r') as fid: 
        feats_segworm = {}
        for name_tierpsy, name_segworm in FEATS_MAT_MAP.items():
            if name_segworm in fid:           
                if not 'eigenProjection' in name_segworm:
                    dd = fid.get_node(name_segworm)
                    if dd != np.dtype('O'):
                        feats_segworm[name_tierpsy] = dd[:]
                    else:
                        if len(dd) == 1:
                            dd = dd[0]
                        feats_segworm[name_tierpsy]=np.array([x[0][0,0] for x in dd])
                        
                else:
                    ii = int(name_tierpsy.replace('eigen_projection_', '')) - 1
                    feats_segworm[name_tierpsy] = fid.get_node(name_segworm)[:, ii]
            else:
                feats_segworm[name_tierpsy] = np.array([np.nan])
        
        for key, val in feats_segworm.items():
            feats_segworm[key] = np.squeeze(val)
            
        
    return feats_segworm

def get_wcon_feats(_data):
    feats_wcon = {key:_data['@OMG ' + key] for key in  FEATS_OW_MAP}
    feats_wcon = {key:np.array(val, np.float) for key, val in  feats_wcon.items() if val is not None}
    return feats_wcon

def read_ow_feats(feats_obj):
    all_feats = {}
    for key, val in FEATS_OW_MAP.items():
        if val in feats_obj._features:
            all_feats[key] = np.array(feats_obj._features[val].value, np.float) 
    return all_feats
#%%
def _plot_indv_feat(feats1, feats2, field, is_hist=False, is_correct=False):
    
    xx = feats1[field]
    if is_correct:
        if 'hips_bend' in field:
            field_c = field.replace('hips_bend', 'neck_bend')
            print('change hips_bend to neck_bend in y-axis')
        elif 'neck_bend' in field:
            field_c = field.replace('neck_bend', 'hips_bend')
            print('change neck_bend to hips_bend in y-axis')
        elif 'path_range' == field:
            field_c = 'path_curvature'
            print('change path_curvature to path_range in y-axis')
        elif 'path_curvature' == field:
            field_c = 'path_range'
            print('change path_range to path_curvature in y-axis')
        
        else:   
            field_c = field
            
        yy = feats2[field_c]
    else:
        yy = feats2[field]
        
    tot = min(xx.size, yy.size)
    xx = xx[:tot]
    yy = yy[:tot]
    
    
    if is_hist:
        dat = np.log2(xx/yy + 1)
        bad = np.isnan(dat) | np.isinf(dat)
        dat = dat[~bad]
        plt.hist(dat)
        plt.title(field)
    else:
        ll = plt.plot(xx, yy, '.', label=field)
        ran1 = plt.ylim()
        ran2 = plt.xlim()
        
        ran_l = ran1 if np.diff(ran1) < np.diff(ran2) else ran2
        
        
        
        plt.plot(ran_l, ran_l, 'k--')
        plt.legend(handles=ll, loc="lower right", fancybox=True)
#%%

def plot_feats_comp(feats1, feats2, is_hist=False, is_correct=False):
    
    tot_f1 = max(feats1[x].size for x in feats1)
    tot_f2 = max(feats2[x].size for x in feats2)
    tot = min(tot_f1, tot_f2)
    
    fields = set(feats1.keys()) & set(feats2.keys())
    ii = 0
    
    sub1, sub2 = 5, 6
    tot_sub = sub1*sub2
    
    all_figs = []
    for field in sorted(fields):
        if feats1[field].size >= tot and feats2[field].size >= tot:            
            if ii % tot_sub == 0:
                fig = plt.figure(figsize=(14,12))
                all_figs.append(fig)
                
            sub_ind = ii%tot_sub + 1
            ii += 1
            plt.subplot(sub1, sub2, sub_ind)
            
            _plot_indv_feat(feats1, feats2, field, is_hist, is_correct)
            
    
    return all_figs
#%%

def _get_skels_segworm(segworm_feat_file):
    #load segworm data
    with tables.File(segworm_feat_file, 'r') as fid:
        segworm_x = -fid.get_node('/worm/posture/skeleton/x')[:]
        segworm_y = -fid.get_node('/worm/posture/skeleton/y')[:]
        skel_segworm = np.stack((segworm_x,segworm_y), axis=2)
    
    skel_segworm = np.rollaxis(skel_segworm, 0, skel_segworm.ndim)
    skel_segworm = np.asfortranarray(skel_segworm)
    
    return skel_segworm

def _align_skeletons(skel_file, skeletons_o, skel_segworm_o):
    print(skeletons_o.shape, skel_segworm_o.shape)
    #load rotation matrix to compare with the segworm
    with tables.File(skel_file, 'r') as fid:
        rotation_matrix = fid.get_node('/stage_movement')._v_attrs['rotation_matrix']
    
    
        microns_per_pixel_scale = fid.get_node(
                '/stage_movement')._v_attrs['microns_per_pixel_scale']
    
    if skel_segworm_o.shape[1] == 2:
        skeletons_o = np.rollaxis(skeletons_o, 2)
        skel_segworm_o = np.rollaxis(skel_segworm_o, 2)
    
    #correct in case the data has different size shape
    max_n_skel = min(skel_segworm_o.shape[0], skeletons_o.shape[0])
    skeletons = skeletons_o[:max_n_skel]
    skel_segworm = skel_segworm_o[:max_n_skel]
    
    # rotate skeleton to compensate for camera movement
    dd = np.sign(microns_per_pixel_scale)
    rotation_matrix_inv = np.dot(
        rotation_matrix * [(1, -1), (-1, 1)], [(dd[0], 0), (0, dd[1])])
    for tt in range(skel_segworm.shape[0]):
        skel_segworm[tt] = np.dot(rotation_matrix_inv, skel_segworm[tt].T).T

    
    #shift the skeletons coordinate system to one that diminushes the errors the most.
    seg_shift = np.nanmedian(skeletons-skel_segworm, axis = (0,1))
    skel_segworm += seg_shift
    print(seg_shift)
    
    if skeletons.shape[-1] == 2:
        skeletons = np.rollaxis(skeletons, 0, skeletons.ndim)
        skel_segworm = np.rollaxis(skel_segworm, 0, skel_segworm.ndim)

    return skeletons, skel_segworm

def plot_skel_diff(skeletons, skel_segworm):
    
    if skel_segworm.shape[1] == 2:
        skeletons = np.rollaxis(skeletons, 2)
        skel_segworm = np.rollaxis(skel_segworm, 2)
    
    delS = skeletons-skel_segworm
    R_error = delS[:,:,0]**2 + delS[:,:,1]**2
    skel_error = np.sqrt(np.mean(R_error, axis=1))
        
        
    w_xlim = w_ylim = (-10, skel_error.size+10)
    plt.figure(figsize=(12, 6))
    plt.subplot(3,2,1)
    plt.plot(skel_error, '.')
    plt.ylim((0, np.nanmax(skel_error)))
    plt.xlim(w_xlim)
    plt.title('')
    plt.ylabel('Error')
    
    plt.subplot(3,2,3)
    plt.plot(skeletons[:,1, 0], 'b')
    plt.plot(skel_segworm[:,1, 0], 'r')
    plt.xlim(w_ylim)
    plt.ylabel('Y coord')
    
    plt.subplot(3,2,5)
    plt.plot(skeletons[:,1, 1], 'b')
    plt.plot(skel_segworm[:,1, 1], 'r')
    plt.xlim(w_xlim)
    plt.ylabel('X coord')
    plt.xlabel('Frame Number')
    
    #plt.figure()
    delT = 1
    plt.subplot(1,2,2)
    plt.plot(skeletons[::delT, 25, 0].T, skeletons[::delT, 25, 1].T, 'b')
    #plt.axis('equal')    
    
    #plt.subplot(1,2,2)
    plt.plot(skel_segworm[::delT, 25, 0].T, skel_segworm[::delT, 25, 1].T, 'r')
    plt.axis('equal') 