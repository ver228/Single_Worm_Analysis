#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 14:42:33 2018

@author: ajaver
"""
import pandas as pd

db_names = ['CeNDR', 'SWDB']
#['F_ow_features_CeNDR.csv' , 'F_ow_features_SWDB.csv']


dat = {}
for db in db_names:
    #dat[db] = pd.read_csv('F_ow_features_{}.csv'.format(db))
    dat[db] = pd.read_csv('F_tierpsy_features_{}.csv'.format(db))
    
#%% common strains
common_strains = set(dat['CeNDR']['strain'].unique()) & set(dat['SWDB']['strain'].unique())

dat_reduced = []
for db in db_names:
    df = dat[db][dat[db]['strain'].isin(common_strains)].copy()
    df['set'] = db
    dat_reduced.append(df)
dat_reduced = pd.concat(dat_reduced)
#%%
import seaborn as sns
import matplotlib.pylab as plt

for feat in ['length_50th', 'speed_10th', 'speed_90th', 'curvature_head_norm_abs_50th', 'eigen_projection_1_abs_50th']:
    #['length_50th', 'midbody_speed_90th', 'midbody_speed_10th', 'eigen_projection_1_50th', 'midbody_bend_mean_90th', 'foraging_amplitude_90th']:
    fig, ax = plt.subplots(figsize = (12, 5))
    #sns.swarmplot('strain', feat, hue='set', data=dat_reduced, ax=ax)
    #sns.stripplot('strain', feat, hue='set', data=dat_reduced, ax=ax, jitter=True)
    sns.boxplot('strain', feat, hue='set', data=dat_reduced, ax=ax)



