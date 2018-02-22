#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 17:41:06 2018

@author: ajaver
"""
import pandas as pd
import numpy as np
import seaborn as sns
import random
import matplotlib.pylab as plt
#%%
#fname = '/Volumes/behavgenom_archive$/Solveig/Results/Experiment1/170714_deve_exp1co3/170714_deve_cohort3_2_Set0_Pos0_Ch4_14072017_160454_features.hdf5'
fname = '/Volumes/behavgenom_archive$/Solveig/Results/Experiment1/170714_deve_exp1co3/170714_deve_cohort3_1_Set0_Pos0_Ch1_14072017_160443_features.hdf5'
#fname = '/Volumes/behavgenom_archive$/Solveig/Results/Experiment1/170714_deve_exp1co3/170714_deve_cohort3_2_Set0_Pos0_Ch4_14072017_160454_featuresN.hdf5'



with pd.HDFStore(fname, 'r') as fid:
    features_timeseries = fid['/features_timeseries']
    #features_timeseries = fid['/timeseries_features']

#%%

feat = 'midbody_speed'
del_T = 25*60
tt = features_timeseries['timestamp']/del_T

tot = tt.max()
features_timeseries['tt_ind'] = np.ceil(tt).astype(np.int)
features_timeseries['timestamp_min'] = tt

features_timeseries_r = features_timeseries[features_timeseries['tt_ind']<=120]

feat_binned = features_timeseries_r.groupby('tt_ind').agg(np.median)
feat_binned_abs = features_timeseries_r.abs().groupby('tt_ind').agg(np.median)
#%%

#%%

#feat = 'speed'

fig = plt.figure(figsize = (12, 10))

plt.subplot(2,1,1)
for _, dat in features_timeseries_r.groupby('worm_index'):
    x = dat['timestamp_min']
    y = dat[feat]
    
    ii = random.random()*0.5 + 0.25
    plt.plot(x,y, color = str(ii))

plt.plot(feat_binned.index, feat_binned[feat], 'r')
plt.xlabel('Time [minutes]')
plt.ylabel('Midbody Speed [$\mu$m/s]')
plt.xlim([0, 120])

#fig = plt.figure(figsize = (12, 5))
plt.subplot(2,1,2)
for _, dat in features_timeseries_r.groupby('worm_index'):
    x = dat['timestamp_min']
    y = dat[feat].abs()
    
    ii = random.random()*0.5 + 0.25
    plt.plot(x,y, color = str(ii))

plt.plot(feat_binned_abs.index, feat_binned_abs[feat], 'r')
plt.xlabel('Time [minutes]')
plt.ylabel('Abs Midbody Speed [$\mu$m/s]')
plt.xlim([0, 120])

fig.savefig('Decreasing Worm Speed.pdf', bbox_inches='tight')
#%% plot the average of several videos...
import os
import glob
dname = '/Volumes/behavgenom_archive$/Solveig/Results/Experiment1/170714_deve_exp1co3/'

feat = 'midbody_speed'
del_T = 25*60

fnames = glob.glob(os.path.join(dname, '*_features.hdf5'))

all_dat = []
for fname in fnames:

    with pd.HDFStore(fname, 'r') as fid:
        features_timeseries = fid['/features_timeseries']
    
    tt = features_timeseries['timestamp']/del_T
    
    tot = tt.max()
    features_timeseries['tt_ind'] = np.ceil(tt).astype(np.int)
    features_timeseries['timestamp_min'] = tt
    
    features_timeseries_r = features_timeseries[features_timeseries['tt_ind']<=120]
    
    feat_binned = features_timeseries_r.groupby('tt_ind').agg(np.median)
    feat_binned_abs = features_timeseries_r.abs().groupby('tt_ind').agg(np.median)

    all_dat.append(feat_binned)

feat_bin_avg = np.mean([x[feat].values for x in all_dat], axis=0)
    
fig = plt.figure(figsize = (12, 5))
for feat_binned in all_dat:
    ii = random.random()*0.5 + 0.25
    plt.plot(feat_binned.index, feat_binned[feat], color = str(ii))

plt.plot(feat_binned.index, feat_bin_avg, 'r', lw=3)

plt.xlabel('Time [minutes]')
plt.ylabel('Midbody Speed [$\mu$m/s]')
plt.xlim([0, 120])
fig.savefig('Average Decreasing Worm Speed.pdf', bbox_inches='tight')


