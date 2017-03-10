#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 12:08:20 2017

@author: ajaver
"""
import os
import glob
import tables
import numpy as np
import matplotlib.pylab as plt
import pandas as pd

from tierpsy.analysis.wcon_export.exportWCON import __addOMGFeat

feats_conv = pd.read_csv('../conversion_table.csv').dropna()
FEATS_MAP = {row['feat_name_tierpsy']:row['feat_name_segworm'] for ii, row in feats_conv.iterrows()}
    

def _get_valid_groups(segworm_feat_file):  
    with tables.File(segworm_feat_file, 'r') as fid:    
        valid_groups = []
        for group in fid.walk_groups("/worm"):
            for array in fid.list_nodes(group, classname='Array'):
                valid_groups.append(array._v_pathname)
    return valid_groups

def _get_skels(feat_file):
    try:
        with tables.File(feat_file, 'r') as fid:
            skeletons = fid.get_node('/coordinates/skeletons')[:]
            frame_range = fid.get_node('/features_events/worm_1')._v_attrs['frame_range']
    
            skeletons = np.pad(skeletons, [(frame_range[0],0), (0,0), (0,0)], 
                           'constant', constant_values = np.nan)
            return skeletons
    except:
        return None
        
def _get_skels_segworm(segworm_feat_file):
    #load segworm data
    with tables.File(segworm_feat_file, 'r') as fid:
        segworm_x = -fid.get_node('/worm/posture/skeleton/x')[:]
        segworm_y = -fid.get_node('/worm/posture/skeleton/y')[:]
        segworm = np.stack((segworm_x,segworm_y), axis=2)
    
    return segworm

def _align_skeletons(skel_file, skeletons_o, skel_segworm_o):
    print(skeletons_o.shape, skel_segworm_o.shape)
    #load rotation matrix to compare with the segworm
    with tables.File(skel_file, 'r') as fid:
        rotation_matrix = fid.get_node('/stage_movement')._v_attrs['rotation_matrix']
    
    
        microns_per_pixel_scale = fid.get_node(
                '/stage_movement')._v_attrs['microns_per_pixel_scale']
    
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

    return skeletons, skel_segworm

def read_feats_segworm(segworm_feat_file):
    with tables.File(segworm_feat_file, 'r') as fid: 
        feats_segworm = {}
        for name_tierpsy, name_segworm in FEATS_MAP.items():
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

def read_feats(feat_file):
    with pd.HDFStore(feat_file, 'r') as fid:
        try:
            features_timeseries = fid['/features_timeseries']
            feats = __addOMGFeat(fid, features_timeseries, worm_id=1)
        except KeyError:
            feats = None
    return feats


def plot_skel_diff(skeletons, skel_segworm):
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
    #%%
    #plt.figure()
    delT = 1
    plt.subplot(1,2,2)
    plt.plot(skeletons[::delT, 25, 0].T, skeletons[::delT, 25, 1].T, 'b')
    #plt.axis('equal')    
    
    #plt.subplot(1,2,2)
    plt.plot(skel_segworm[::delT, 25, 0].T, skel_segworm[::delT, 25, 1].T, 'r')
    plt.axis('equal') 


if __name__ == '__main__':
#    conn = pymysql.connect(host='localhost', db = 'single_worm_db')
#    cur = conn.cursor()
#    sql = '''
#    SELECT id, results_dir, base_name
#    FROM experiments
#    WHERE exit_flag_id > (SELECT f.id FROM exit_flags AS f WHERE name = "FEAT_CREATE")
#    AND exit_flag_id < 100
#    '''
#    cur.execute(sql)
#    results = cur.fetchall()
    
    
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    f_list = glob.glob(os.path.join(main_dir, '*_features.mat'))
    
    #dd = [_get_valid_groups(x) for x in f_list]
    #f_list = [f_list[x] for x in [2,3]]#[21, 36, 48]]
    
    for segworm_feat_file in f_list:        
        print(segworm_feat_file)
        feat_file = segworm_feat_file.replace('_features.mat', '_features.hdf5')
        skel_file = segworm_feat_file.replace('_features.mat', '_skeletons.hdf5')
        

        if not all(os.path.exists(x) for x in [feat_file, skel_file, segworm_feat_file]):
            continue
        
        skeletons = _get_skels(feat_file)
        skel_segworm = _get_skels_segworm(segworm_feat_file)
        
        if skeletons is None:
            continue
        
        skeletons, skel_segworm = _align_skeletons(skel_file, skeletons, skel_segworm)
        plot_skel_diff(skeletons, skel_segworm)
        
        
#        #%%
#        feats_segworm = read_feats_segworm(segworm_feat_file)
#        feats = read_feats(feat_file)
#        fields = set(feats.keys()) & set(feats_segworm.keys())
#        for x in sorted(fields):
#            N1 = 1 if isinstance(feats[x], (int,float)) else feats[x].shape
#            N2 = 1 if isinstance(feats_segworm[x], (int,float)) else feats_segworm[x].shape
#            print(x, N1, N2)
#            
#        #%%
#        tot = skeletons.shape[0]
#        plt.figure()
#                
#        ii = 0
#        for field in sorted(fields):
#            if feats[field].shape[0] >= tot:
#                ii += 1
#                plt.subplot(6, 10, ii)
#                xx = feats[field][:tot]
#                yy = feats_segworm[field][:tot]
#                
#                plt.plot(xx, yy, '.')
#                plt.plot(plt.xlim(), plt.xlim(), 'k--')
#                plt.title(field)
        #%%
        
        #%%
        