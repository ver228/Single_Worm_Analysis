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

feats_conv = pd.read_csv('conversion_table.csv').dropna()
FEATS_MAT_MAP = {row['feat_name_tierpsy']:row['feat_name_segworm'] for ii, row in feats_conv.iterrows()}
FEATS_OW_MAP = {row['feat_name_tierpsy']:row['feat_name_openworm'] for ii, row in feats_conv.iterrows()}



class FeatsReader():
    def __init__(self, feat_file):
        self.feat_file = feat_file
    
    @property
    def features_events(self):
        try:
            return self._features_events
        except:
            with tables.File(self.feat_file, 'r') as fid:
            
                features_events = {}
                node = fid.get_node('/features_events')
                for worn_n in node._v_children.keys():
                    worm_node = fid.get_node('/features_events/' + worn_n)
                    
                    for feat in worm_node._v_children.keys():
                        if not feat in features_events:
                            features_events[feat] = {}
                        dat = fid.get_node(worm_node._v_pathname, feat)[:]
                        features_events[feat][worn_n] = dat
            
            
            self._features_events = features_events
            return self._features_events
    
    @property
    def features_events_plate(self):
        def dict2array(dd):
            return np.concatenate([val for val in dd.values()])
        return {feat:dict2array(val) for feat, val in self.features_events.items()}
    
    @property
    def features_timeseries(self):
        try:
            return self._features_timeseries
        except:
            with pd.HDFStore(self.feat_file, 'r') as fid:
                self._features_timeseries = fid['/features_timeseries']
            return self._features_timeseries
    
    
    def read_plate_features(self):
        dd = {x:self.features_timeseries[x].values for x in self.features_timeseries}
        worm_features_dict = {**dd, **self.features_events_plate}
        return worm_features_dict
    
    def get_worm_coord(self, worm_index, field_name):
        good_rows = self.features_timeseries['worm_index'] == worm_index
        rows_indexes = good_rows.index.values[good_rows.values]
    
        
        with tables.File(self.feat_file, 'r') as fid:
            skeletons = fid.get_node('/coordinates/' + field_name)[rows_indexes, : , :]
        return skeletons
    
   
    
    
class FeatsReaderComp(FeatsReader): 
    def __init__(self, feat_file, segworm_feat_file='', skel_file=''):
        if not segworm_feat_file:
            segworm_feat_file = feat_file.replace('.hdf5', '.mat')
        
        if not skel_file:
            skel_file = feat_file.replace('_features.hdf5', '_skeletons.hdf5')
        
        self.skel_file = skel_file
        self.segworm_feat_file = segworm_feat_file
        super().__init__(feat_file)
    
    def read_feats_segworm(self, correct_misnamed = True):
        with tables.File(self.segworm_feat_file, 'r') as fid: 
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
        if correct_misnamed:
            feats2switch = [('hips_bend_mean', 'neck_bend_mean'),
                        ('hips_bend_sd', 'neck_bend_sd'),
                        ('path_curvature', 'path_range')]
    
            for feat1, feat2 in feats2switch:
                feats_segworm[feat1], feats_segworm[feat2] = feats_segworm[feat2], feats_segworm[feat1]
        
        return feats_segworm
        
    
    @property
    def skels_segworm(self):
        try:
            return self._skels_segworm
        except:
            #load segworm data
            with tables.File(self.segworm_feat_file, 'r') as fid:
                segworm_x = -fid.get_node('/worm/posture/skeleton/x')[:]
                segworm_y = -fid.get_node('/worm/posture/skeleton/y')[:]
                skel_segworm = np.stack((segworm_x,segworm_y), axis=2)
            
            skel_segworm = np.rollaxis(skel_segworm, 0, skel_segworm.ndim)
            skel_segworm = np.asfortranarray(skel_segworm)
            
            self._skels_segworm = np.rollaxis(skel_segworm, 2, 0)
            return self._skels_segworm
    
    @property
    def skeletons(self):
        try:
            return self._skeletons
        except:
            #load segworm data
            self._skeletons = self.get_worm_coord(1, 'skeletons')
            return self._skeletons


    def read_skeletons(self):
        return self._align_skeletons(self.skel_file, self.skeletons, self.skels_segworm)
    
    def _align_skeletons(self, skel_file, skeletons, skel_segworm):
            #load rotation matrix to compare with the segworm
            with tables.File(skel_file, 'r') as fid:
                rotation_matrix = fid.get_node('/stage_movement')._v_attrs['rotation_matrix']
            
            
                microns_per_pixel_scale = fid.get_node(
                        '/stage_movement')._v_attrs['microns_per_pixel_scale']
            
            # rotate skeleton to compensate for camera movement
            dd = np.sign(microns_per_pixel_scale)
            rotation_matrix_inv = np.dot(
                rotation_matrix * [(1, -1), (-1, 1)], [(dd[0], 0), (0, dd[1])])
            for tt in range(skel_segworm.shape[0]):
                skel_segworm[tt] = np.dot(rotation_matrix_inv, skel_segworm[tt].T).T
        
            max_n_skel = min(skel_segworm.shape[0], skeletons.shape[0])
            #shift the skeletons coordinate system to one that diminushes the errors the most.
            dskel = skeletons[:max_n_skel]-skel_segworm[:max_n_skel]
            seg_shift = np.nanmedian(dskel, axis = (0,1))
            skel_segworm += seg_shift
            
            return skeletons, skel_segworm



#%%
def _plot_indv_feat(feats1, feats2, field, add_name=True, is_hist=False):
    xx = feats1[field]
    yy = feats2[field]
    
    tot = min(xx.size, yy.size)
    xx = xx[:tot]
    yy = yy[:tot]
    
    
    if is_hist:
        xx = xx[~np.isnan(xx)]
        yy = yy[~np.isnan(yy)]
        
        bot = min(np.min(xx), np.min(yy))
        top = max(np.max(xx), np.max(yy))
        
        bins = np.linspace(bot, top, 100)
        
        count_x, _ = np.histogram(xx, bins)
        count_y, _ = np.histogram(yy, bins)
        
        l1 = plt.plot(bins[:-1], count_x)
        l2 = plt.plot(bins[:-1], count_y)
        if add_name:
            my = max(np.max(count_x), np.max(count_y))*0.95
            mx = bins[1]
            plt.text(mx, my, field)
            #plt.title(field)
        return (l1, l2)
    else:
        ll = plt.plot(xx, yy, '.', label=field)
        ran1 = plt.ylim()
        ran2 = plt.xlim()
        
        ran_l = ran1 if np.diff(ran1) < np.diff(ran2) else ran2
        
        plt.plot(ran_l, ran_l, 'k--')
        if add_name:
            my = (ran1[1]-ran1[0])*0.97 + ran1[0]
            mx = (ran2[1]-ran2[0])*0.03 + ran2[0]
            plt.text(mx, my, field)
        
        return ll
        #plt.legend(handles=ll, loc="lower right", fancybox=True)
        #plt.axis('equal')
#%%

def plot_feats_comp(feats1, feats2, is_hist=False):
    
    tot_f1 = max(feats1[x].size for x in feats1)
    tot_f2 = max(feats2[x].size for x in feats2)
    tot = min(tot_f1, tot_f2)
    
    fields = set(feats1.keys()) & set(feats2.keys())
    ii = 0
    
    sub1, sub2 = 5, 6
    tot_sub = sub1*sub2
    
    all_figs = []
    for field in sorted(fields):
        if feats1[field].size == 1 or feats2[field].size == 1:
            continue
        
        if is_hist and \
        not (feats1[field].size >= tot and feats2[field].size >= tot):
            continue
        
            
        if ii % tot_sub == 0:
            fig = plt.figure(figsize=(14,12))
            all_figs.append(fig)
            
        sub_ind = ii%tot_sub + 1
        ii += 1
        plt.subplot(sub1, sub2, sub_ind)
        
        
        _plot_indv_feat(feats1, feats2, field, is_hist)
        
    
    return all_figs
#%%

if __name__ == '__main__':
    
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    #base_name = 'N2 on food L_2010_02_26__08_44_59___7___1'
    base_name = 'unc-7 (cb5) on food R_2010_09_10__15_17_34___7___9'
    #base_name = 'N2 on food R_2011_09_13__11_59___3___3'
    #base_name = 'N2 on food R_2010_10_15__15_36_54___7___10'
    
    feat_mat_file = os.path.join(main_dir, base_name + '_features.mat')
    skel_file = os.path.join(main_dir, base_name + '_skeletons.hdf5')
    feat_file = os.path.join(main_dir, base_name + '_features.hdf5')
    segworm_feat_file = os.path.join(main_dir, '_segworm_files', base_name + '_features.mat')
    
    feats_reader = FeatsReaderComp(feat_file, segworm_feat_file)
    
    tierpsy_feats = feats_reader.read_plate_features()
    segworm_feats = feats_reader.read_feats_segworm()

    #plot_feats_comp(tierpsy_feats, segworm_feats)
    #plot_feats_comp(tierpsy_feats, segworm_feats, is_hist=True)
    #%%
    all_fields = sorted([val for key,val in FEATS_OW_MAP.items()])
    rev_dict = {val:key for key,val in FEATS_OW_MAP.items()}
    
    for ow_field in all_fields:
        field = rev_dict[ow_field]
        if tierpsy_feats[field].size == 1 or segworm_feats[field].size == 1:
            continue
        
        plt.figure(figsize=(10,5))
        plt.subplot(1,2,1)
        _plot_indv_feat(tierpsy_feats, segworm_feats, field, add_name=False, is_hist=False)
        plt.xlabel('tierpsy features')
        plt.ylabel('segworm features')
        
        
        plt.subplot(1,2,2)
        ax = _plot_indv_feat(tierpsy_feats, segworm_feats, field, add_name=False, is_hist=True)
        L=plt.legend(ax)
        for ii, ff in enumerate(('tierpsy features', 'segworm features')):
            L.get_texts()[ii].set_text(ff)
        
        plt.suptitle(ow_field)
        
    
    #%%
    #plt.figure()
    #_plot_indv_feat(tierpsy_feats, segworm_feats, "length", is_hist=True)
    #%%
#    feats1, feats2 = tierpsy_feats, segworm_feats
#    
#    tot_f1 = max(feats1[x].size for x in feats1)
#    tot_f2 = max(feats2[x].size for x in feats2)
#    tot = min(tot_f1, tot_f2)
#    
#    xx = feats1['midbody_bend_mean']
#    yy = feats2['midbody_bend_mean']
#    
#    xx = xx[:tot]
#    yy = yy[:tot]
#    
#    plt.plot(xx)
#    plt.plot(yy)
#    
#    #plt.plot(xx, yy, '.')
    #%%
    
#    if is_correct:
#        if 'hips_bend' in field:
#            field_c = field.replace('hips_bend', 'neck_bend')
#            print('change hips_bend to neck_bend in y-axis')
#        elif 'neck_bend' in field:
#            field_c = field.replace('neck_bend', 'hips_bend')
#            print('change neck_bend to hips_bend in y-axis')
#        elif 'path_range' == field:
#            field_c = 'path_curvature'
#            print('change path_curvature to path_range in y-axis')
#        elif 'path_curvature' == field:
#            field_c = 'path_range'
#            print('change path_range to path_curvature in y-axis')
#        
#        else:   
#            field_c = field
#            
#        yy = feats2[field_c]
#    else:
#        
        