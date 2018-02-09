#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 17:23:22 2017

@author: ajaver
"""

import pandas as pd
import pymysql
import os

from tierpsy_features.summary_stats import get_feat_stats, _filter_ventral_features, get_df_quantiles
from tierpsy_features import timeseries_feats_columns
from tierpsy.helper.params import read_ventral_side

def _get_all_stats(timeseries_data, blob_features):
    feat_stats = get_feat_stats(timeseries_data, fps, is_normalize = False)
        
    #this is a dirty solution to avoid duplicates but we are testing right now
    feat_stats_n = get_feat_stats(timeseries_data, fps, is_normalize = True)
    feat_stats_n = feat_stats_n[[x for x in feat_stats_n.index if x not in feat_stats.index]]
    
    # another dirty solution to add features with ventral sign
    ventral_feats = _filter_ventral_features(timeseries_feats_columns)
    if ventral_side == 'clockwise':
        timeseries_data[ventral_feats] *= -1
    
    feat_stats_v = get_df_quantiles(timeseries_data, 
                     feats2check = ventral_feats, 
                     is_abs_ventral = False, 
                     is_normalize = False)
    
    
    feat_stats_v_n = get_df_quantiles(timeseries_data, 
                     feats2check = ventral_feats, 
                     is_abs_ventral = False, 
                     is_normalize = True)
    feat_stats_v_n = feat_stats_v_n[[x for x in feat_stats_v_n.index if x not in feat_stats_v.index]]
    
    blob_feats = [
           'area', 'perimeter', 'box_length', 'box_width',
           'quirkiness', 'compactness', 'solidity',
           'hu0', 'hu1', 'hu2', 'hu3', 'hu4',
           'hu5', 'hu6'
           ]
    blob_stats = get_df_quantiles(blob_features, feats2check = blob_feats)
    blob_stats.index = ['blob_' + x for x in blob_stats.index]
    
    exp_feats = pd.concat((feat_stats, feat_stats_n, blob_stats, feat_stats_v, feat_stats_v_n))
    
    return exp_feats

if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    sql ='''
    DROP TABLE IF EXISTS tierpsy_features;
    CREATE TABLE `tierpsy_features` (
    `experiment_id` INT NOT NULL,
    `name` VARCHAR(100),
    `value` FLOAT,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
    )
    '''
    cur.execute(sql)
    
    sql = '''SELECT *
    FROM experiments_valid
    '''
    cur.execute(sql)
    all_rows = cur.fetchall()
    
    for ii, row in enumerate(all_rows):
        print(ii+1, len(all_rows))
        
        mask_file = os.path.join(row['results_dir'], row['base_name'] + '.hdf5')
        features_file = os.path.join(row['results_dir'], row['base_name'] + '_featuresN.hdf5')
        
        if not os.path.exists(features_file):
            continue
        
        ventral_side = read_ventral_side(mask_file)
        
        with pd.HDFStore(features_file, 'r') as fid:
            if '/timeseries_data' in fid:
                field = '/timeseries_data'
            else:
                #error due to a change of name
                field = '/timeseries_features'
            
            fps = fid.get_storer('/trajectories_data').attrs['fps']
            timeseries_data = fid[field]
            blob_features = fid['/blob_features']
        
        
        exp_feats = _get_all_stats(timeseries_data, blob_features)
        
        #%%
        values_l = [x if x==x else None for x in exp_feats.values.tolist()]
        name_l = exp_feats.index.tolist()
        exp_id_l = len(exp_feats)*[row['id']]
        rows2insert = list(zip(exp_id_l, name_l, values_l))
        #%%
        sql = '''
        INSERT INTO tierpsy_features (experiment_id, name, value) 
        VALUES (%s, %s, %s)
        '''
        cur.executemany(sql, rows2insert)
        
        conn.commit()
        #print('ERROR!!!', row['id'], row['base_name'])
            
    