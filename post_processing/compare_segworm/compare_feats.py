#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 18:35:13 2017

@author: ajaver
"""
import os
import tables
import numpy as np
#import matplotlib.pylab as plt
import pandas as pd
import open_worm_analysis_toolbox as mv
from WormFromWCON import WormFromWCON

feats_conv = pd.read_csv('conversion_table.csv').dropna()
FEATS_MAT_MAP = {row['feat_name_tierpsy']:row['feat_name_segworm'] for ii, row in feats_conv.iterrows()}
FEATS_OW_MAP = {row['feat_name_tierpsy']:row['feat_name_openworm'] for ii, row in feats_conv.iterrows()}

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
    #I need the _skeletons.hdf5 file get the rotation matrix needed to 
    #align the skeletons in the old mat files with the new hdf5 files. 
    
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
    #%%


def get_wcon_feats(_data):
    feats_wcon = {key:_data['@OMG ' + key] for key in  FEATS_OW_MAP}
    feats_wcon = {key:np.array(val, np.float) for key, val in  feats_wcon.items() if val is not None}
    return feats_wcon
#%%
def plot_feats_comp(feats1, feats2):
    tot = min(feats1['length'].size, feats2['length'].size)
    fields = set(feats1.keys()) & set(feats2.keys())
    ii = 0
    
    sub1, sub2 = 5, 6
    tot_sub = sub1*sub2
    
    all_figs = []
    for field in sorted(fields):
        if feats1[field].size >= tot:            
            if ii % tot_sub == 0:
                fig = plt.figure(figsize=(14,12))
                all_figs.append(fig)
                
            sub_ind = ii%tot_sub + 1
            
            ii += 1
            plt.subplot(sub1, sub2, sub_ind)
            
            xx = feats1[field][:tot]
            yy = feats2[field][:tot]
            
            ll = plt.plot(xx, yy, '.', label=field)
            plt.plot(plt.xlim(), plt.xlim(), 'k--')
            #plt.title(field)
            plt.legend(handles=ll, loc="lower right", fancybox=True)
            
    return all_figs


#%%
if __name__ == '__main__':
    
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    #base_name = 'N2 on food L_2010_08_03__10_17_54___7___1'
    base_name = 'N2 on food R_2011_09_13__11_59___3___3'
    #base_name = 'N2 on food R_2010_10_15__15_36_54___7___10'
    
    if False:    
        from tierpsy.analysis.wcon_export.exportWCON import exportWCON
        feat_file = os.path.join(main_dir, base_name + '_features.hdf5')
        exportWCON(feat_file, READ_FEATURES=True)
    
    feat_mat_file = os.path.join(main_dir, base_name + '_features.mat')
    wcon_file = os.path.join(main_dir, base_name + '.wcon.zip')
    skel_file = os.path.join(main_dir, base_name + '_skeletons.hdf5')
    
    nw = WormFromWCON(wcon_file)
    wf = mv.WormFeatures(nw)
    #%%
    feats_mat = read_feats_segworm(feat_mat_file)
    feats_wcon = get_wcon_feats(nw._wcon_feats['data'][0])
    feats_ow = {key:np.array(wf._features[val].value, np.float) for key, val in  FEATS_OW_MAP.items()}
    #%%
    
    #%%
    import matplotlib.pyplot as plt
    
    
    save_path = '/Users/ajaver/Documents/GitHub/single-worm-analysis/post_processing/compare_segworm'
    
    for name, feats_d in [('tierpsy', feats_ow), ('schafer', feats_mat)]:
        all_figs = plot_feats_comp(feats_wcon, feats_d)
        for ii, fig in enumerate(all_figs):
            fig.savefig('{}/WCON_vs_{}_{}.png'.format(save_path, name, ii+1), bbox_inches='tight')
        
    
        

#%%
#tot = min(feats_mat['length'].size, feats_ow['length'].size, feats_wcon['length'].size)
#
#for feat_dic in [feats_ow, feats_wcon]:
#    #plt.figure()
#    plt.plot(feats_mat['length'][:tot], feat_dic['length'][:tot], '.')
#    plt.plot(plt.xlim(), plt.xlim(), 'k--')