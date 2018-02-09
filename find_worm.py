#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 09:49:00 2017

@author: ajaver
"""

import pymysql
import pandas as pd


conn = pymysql.connect(host='localhost', database='single_worm_db')
sql = '''
select f.*, ev.*, e.youtube_id
from features_means as f 
join experiments_valid as ev on ev.id = f.experiment_id 
join experiments as e on e.id = ev.id
where total_time > 300
'''
df = pd.read_sql(sql, con=conn)

#%%

feat_v = 'midbody_bend_mean_abs'
th = 20

#df_e = df[df['midbody_bend_sd_abs']>29]
df_e = df[df[feat_v]>th]
#df_e = df[df['eccentricity']<0.8]

#df_e = df_e.drop_duplicates('strain')
#%%
import os
import tables
import matplotlib.pylab as plt

#%%
df_e = df_e.sort_values(by=['strain', feat_v])
for irow, row in df_e.iterrows():
    if row['youtube_id'] is None:
        continue
    
    if row['strain'] not in ['DR1089', 'AQ2934', 'QT309']:#, 'DR1089', 'MT22464', 'CB678']:
        continue
    
    fname = os.path.join(row['results_dir'], row['base_name'] + '.hdf5')
    print(fname)
    
    fname = os.path.join(row['results_dir'], row['base_name'] + '_features.hdf5')    
    with pd.HDFStore(fname, 'r') as fid:
        features_timeseries = fid['/features_timeseries']
        
    vv = features_timeseries.index[features_timeseries['motion_modes'] == 1]
    
    if len(vv) == 0:
        continue
    print(len(vv))
    print('https://www.youtube.com/watch?v={}'.format(row['youtube_id']))
    
    with tables.File(fname, 'r') as fid:
        skeletons = fid.get_node('/coordinates/skeletons')[vv]
    
    
    plt.figure()
    plt.plot(skeletons[0::50, :, 0].T, skeletons[0::50, :, 1].T)
    plt.axis('equal')
    plt.title(row['strain'] + '\n' + row['base_name'])

#%%
sql = '''
select youtube_id  
from experiments 
where strain_id = (select id from strains where name = 'DR1089');
'''
youtube_ids = pd.read_sql(sql, con=conn)['youtube_id']

for youtube_id in youtube_ids:
    if youtube_id is not None:    
        print('https://www.youtube.com/watch?v={}'.format(youtube_id))


    #%%
    
    
    