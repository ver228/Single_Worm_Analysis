#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 18:57:32 2018

@author: ajaver
"""

import pandas as pd
import tables
import matplotlib.pylab as plt
import numpy as np

#REGION_LABELS = {'after': 1,
# 'before': 0,
# 'inter_pulses_1': 8,
# 'inter_pulses_2': 9,
# 'inter_pulses_3': 10,
# 'inter_pulses_4': 11,
# 'inter_pulses_5': 12,
# 'long_pulse': 2,
# 'short_pulse_1': 3,
# 'short_pulse_2': 4,
# 'short_pulse_3': 5,
# 'short_pulse_4': 6,
# 'short_pulse_5': 7}
#
#AQ2028 - to goes back a lot...
#
#
#'curvature_midbody'
#
#curvature_head_10th
if __name__ == '__main__':
    exp_df_l = pd.read_csv('exp_info.csv', index_col=0)
    #exp_df_l = exp_df_l[~exp_df_l['day'].isin(['day1'])]
    exp_df_l = exp_df_l[exp_df_l['day'] == 'day10']
    
    #strains = ('AQ2028', 'AQ2052', 'AQ2232', 'AQ2235', 'HBR222', 'HBR520')
    strains = ('AQ2052',)
    
    
    
    plt.figure(figsize=(12,7))
    for ss in strains:
        tot = 0
        exp_df = exp_df_l[exp_df_l['strain'] == ss]
        
        # Just for debugging, if i do not find pulses it will show some graphs
        problem_files = exp_df.loc[~exp_df['has_valid_light'], 'mask_file'].values
        
        gg = exp_df.groupby('day')
        
        #select a specific day
        dat = gg.get_group('day10') 
        
        #exp_df.sort_values(by=['day', 'exp_type'])
        for _, row in dat.iterrows():
            mask_file = row['mask_file']
            with tables.File(mask_file) as fid:
                mean_intensity = fid.get_node('/mean_intensity')[:]
            
            
            #feat_file = mask_file.replace('.hdf5', '_featuresN.hdf5').replace('MaskedVideos', 'Results')
            feat_file = mask_file.replace('.hdf5', '_features.hdf5').replace('MaskedVideos', 'Results')
            
            with pd.HDFStore(feat_file) as fid:
                timeseries_data = fid['/features_timeseries']
            
                #timeseries_data = fid['/timeseries_data']
            
            #curv_feats = [x for x in timeseries_data.columns if 'curvature' in x]
            bend_feats = [x for x in timeseries_data.columns if 'bend' in x]
            timeseries_data[bend_feats] = timeseries_data[bend_feats].abs()
            
            del_T = 25*5
            tt = timeseries_data['timestamp']/del_T
            timeseries_data['tt_ind'] = np.ceil(tt).astype(np.int)
            timeseries_data['timestamp_min'] = tt
            
            #feat_binned = timeseries_data.groupby('tt_ind').agg(np.median)
            feat_binned = timeseries_data.groupby('tt_ind').agg(np.mean)
            
            #feat_name = 'speed'
            #feat_name = 'turn'
            #feat_name = 'curvature_tail'
            #feat_name = 'curvature_head'
            #feat_name = 'speed'
            
            #ylim_d = {
            #        'curvature_tail': (0, 9e-3), 
            #        'speed': (-250, 250), 
            #        'turn': (0, 0.8)
            #        }
            
            ylim_d = {
                    'midbody_speed': [(-320, 320), 'Mibody Speed [$\mu$m/s]'],
                    'tail_bend_mean' : [(0, 50), 'Tail Bend Mean [deg]']
                    }
            
            
            for i_feat, (feat_name, (y_ll, lab_s)) in enumerate(ylim_d.items()):
                
                i_exp = int(row['exp_type'] == 'ATR')
                plt.subplot(2,2, i_feat*2 + i_exp + 1)
                
                y = timeseries_data[feat_name]
                y_f = feat_binned[feat_name]
                
                y_ind = mean_intensity-mean_intensity.min()
                y_ind = y_ind/y_ind.max()
                
                y_ind = y_ind*(y_ll[1] - y_ll[0]) + y_ll[0]
                
                #fig = plt.figure(figsize=(12,5))
                
                
                xx = np.arange(y_ind.size)/25
                plt.plot(xx, y_ind, 'r', lw=0.75)
                plt.plot(feat_binned.index*del_T/25, y_f, '.-', lw=2)
                
                plt.ylim(*y_ll)
                plt.xlim(0, 900)
                #3s_t = '{} {} {} {}'.format(row['exp_type'], feat_name, row['strain'],  row['day'])
                if i_feat == 0:
                    plt.title(row['exp_type'])
                
                plt.ylabel(lab_s)
                plt.xlabel('Time [s]')
                #fig.savefig(s_t + '.pdf')
            
        plt.suptitle(ss)
    
    plt.savefig('{}_{}.pdf'.format(row['strain'], row['day']), bbox_inches='tight')
    