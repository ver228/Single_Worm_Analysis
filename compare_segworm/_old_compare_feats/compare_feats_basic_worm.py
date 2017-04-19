#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 18:35:13 2017

@author: ajaver
"""
import os
import tables
import numpy as np
import matplotlib.pylab as plt
import pandas as pd
import open_worm_analysis_toolbox as mv
import zipfile
import json

feats_conv = pd.read_csv('conversion_table.csv').dropna()
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
#%%
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
#%%    


def get_wcon_feats(_data):
    feats_wcon = {key:_data['@OMG ' + key] for key in  FEATS_OW_MAP}
    feats_wcon = {key:np.array(val, np.float) for key, val in  feats_wcon.items() if val is not None}
    return feats_wcon

def plot_feats_comp(feats1, feats2, is_hist=False):
    
    tot = min(feats1['length'].size, feats2['length'].size)
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
            
            xx = feats1[field][:tot]
            yy = feats2[field][:tot]
            
            if is_hist:
                dat = np.log2(xx/yy + 1)
                bad = np.isnan(dat) | np.isinf(dat)
                dat = dat[~bad]
                plt.hist(dat)
                plt.title(field)
            else:
                ll = plt.plot(xx, yy, '.', label=field)
                plt.plot(plt.xlim(), plt.xlim(), 'k--')
                plt.legend(handles=ll, loc="lower right", fancybox=True)
    
    return all_figs
#%%
def _read_repack(field_x, _data):
    field_y = field_x.replace('x', 'y')
    dat =  np.stack((_data[field_x], _data[field_y]), axis=2).astype(np.float)
    
    #the openworm toolbox requires 49x2xn
    # roll axis to have it as 49x2xn
    dat = np.rollaxis(dat, 0, dat.ndim)
    # change the memory order so the last dimension changes slowly
    dat = np.asfortranarray(dat)
    
    return dat
#%%
def read_ow_feats(feats_obj):
    all_feats = {}
    for key, val in FEATS_OW_MAP.items():
        if val in feats_obj._features:
            all_feats[key] = np.array(feats_obj._features[val].value, np.float) 
    return all_feats

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
#%%
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
#%%
def save_figs(all_figs, save_path, save_name):
    for ii, fig in enumerate(all_figs):
        str_t = '{}_{}'.format(save_name, ii+1)
        fig.suptitle(str_t)
        fig.savefig('{}/{}.png'.format(save_path, str_t), bbox_inches='tight')
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
    
    #%%
    with zipfile.ZipFile(wcon_file, mode='r') as zf:
        fname = os.path.basename(wcon_file).replace('.zip', '')
        wcon_txt = zf.read(fname).decode("utf-8")
    _wcon_feats = json.loads(wcon_txt)
    _data = _wcon_feats['data'][0]
    
    timestamp = np.array(_data['t']).astype(np.float)
    skeleton = _read_repack('x', _data)
    ventral_contour = _read_repack('@OMG x_ventral_contour', _data)
    dorsal_contour = _read_repack('@OMG x_dorsal_contour', _data)
    skeletons_o = _read_repack('x', _data)
    
    print('Calculating features from WCON contour...')
    bw = mv.BasicWorm.from_contour_factory(ventral_contour, dorsal_contour);
    nw = mv.NormalizedWorm.from_BasicWorm_factory(bw)
    wf = mv.WormFeatures(nw)
    
    #%%
    #Align skeletons
    skel_segworm_o = _get_skels_segworm(feat_mat_file)
    skeletons, skel_segworm = _align_skeletons(skel_file, skeletons_o, skel_segworm_o)
    plot_skel_diff(skeletons, skel_segworm)
    #%%
    print('Calculating features from skeletons in the features.mat ...')
    bw_mat = mv.BasicWorm.from_skeleton_factory(skel_segworm);
    nw_mat = mv.NormalizedWorm.from_BasicWorm_factory(bw_mat)
    wf_mat = mv.WormFeatures(nw_mat)
    
    bw_mat2 = mv.BasicWorm.from_skeleton_factory(nw.skeleton);
    nw_mat2 = mv.NormalizedWorm.from_BasicWorm_factory(bw_mat2)
    wf_mat2 = mv.WormFeatures(nw_mat2)
    
    bw_mat3 = mv.BasicWorm.from_skeleton_factory(skeletons);
    nw_mat3 = mv.NormalizedWorm.from_BasicWorm_factory(bw_mat3)
    wf_mat3 = mv.WormFeatures(nw_mat3)
    
    #%%
    feats_mat = read_feats_segworm(feat_mat_file)
    feats_ow = read_ow_feats(wf)
    feats_ow_mat = read_ow_feats(wf_mat)
    feats_ow_mat2 = read_ow_feats(wf_mat2)
    feats_ow_mat3 = read_ow_feats(wf_mat3)
    #%%
    save_path = '/Users/ajaver/Documents/GitHub/single-worm-analysis/post_processing/compare_segworm'
    all_figs = plot_feats_comp(feats_mat, feats_ow)
    save_figs(all_figs, save_path, 'Schafer_vs_OWCNT')
    #%%
    all_figs = plot_feats_comp(feats_mat, feats_ow_mat)
    save_figs(all_figs, save_path, 'Schafer_vs_OWSKEL')
    #%%
    all_figs = plot_feats_comp(feats_ow, feats_ow_mat)
    save_figs(all_figs, save_path, 'OWCNT_vs_OWSKEL')

    #%%
    all_figs = plot_feats_comp(feats_ow, feats_ow_mat2)
    save_figs(all_figs, save_path, 'OWCNT_vs_OWSKEL2')
    #%%
    all_figs = plot_feats_comp(feats_ow_mat, feats_ow_mat3)
    save_figs(all_figs, save_path, 'OWSKEL_vs_OWSKEL3')

    #%%
    all_figs = plot_feats_comp(feats_ow_mat2, feats_ow_mat3)
    save_figs(all_figs, save_path, 'OWSKEL2_vs_OWSKEL3')    
    #%%
    plt.figure(figsize=(10,10))
    for ii in range(12):
        
        ss = 26815 + ii#*1000
        ax = plt.subplot(3,4, ii+1)
        plt.plot(nw.skeleton_x[:, ss], nw.skeleton_y[:, ss], '.b')
        plt.plot(nw.dorsal_contour_x[:, ss], nw.dorsal_contour_y[:, ss], 'b')
        plt.plot(nw.ventral_contour_x[:, ss], nw.ventral_contour_y[:, ss], 'b')
        plt.plot(nw_mat.skeleton_x[:, ss], nw_mat.skeleton_y[:, ss], '.r')
        
        if nw_mat.dorsal_contour is not None:
            plt.plot(nw_mat.dorsal_contour_x[:, ss], nw_mat.dorsal_contour_y[:, ss], 'r')
            plt.plot(nw_mat.ventral_contour_x[:, ss], nw_mat.ventral_contour_y[:, ss], 'r')
            
        plt.axis('equal')
        plt.axis('off')
        ax.text(0.2, 0.01, 
                'frame_n = {}'.format(ss), 
                verticalalignment='bottom', 
                horizontalalignment='left',
                transform=ax.transAxes,
                color='k')
        
    plt.savefig('{}/WORM_OUTLINES.png'.format(save_path), bbox_inches='tight')
    
    #%%
    plt.figure(figsize=(10,10))
    for ii in range(12):
        
        ss = 26815#ii*1000
        ax = plt.subplot(3,4, ii+1)
        plt.plot(nw.angles[:, ss], '.-b')
        plt.plot(nw_mat.angles[:, ss], '.-r')
        
        plt.axis('equal')
        plt.axis('off')
        ax.text(0.2, 0.01, 
                'frame_n = {}'.format(ss), 
                verticalalignment='bottom', 
                horizontalalignment='left',
                transform=ax.transAxes,
                color='k')
    #%%
#    diff_ang = (nw_mat.angles)/(nw_mat3.angles)
#    plt.plot(diff_ang.flat, '.')