#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:46:03 2017

@author: ajaver
"""
import requests
import pymysql
import json

from MWTracker.analysis.vid_subsample.createSampleVideo import getSubSampleVidName
from MWTracker.analysis.wcon_export.exportWCON import getWCOName


if __name__ == '__main__':
    
    
    speed_up = 8
    youtube_privacy_status='private'
    
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    
    sql = '''SELECT experiment_id, mask_file, skeletons_file, features_file
    FROM progress_analysis 
    WHERE (exit_flag_id = 
    (SELECT f.id FROM exit_flags as f WHERE checkpoint='END'))'''
    cur.execute(sql)
    results = cur.fetchall()
    
    

    CLIENT_SECRETS_FILE = "client_secrets.txt"
    ZENODO_SCOPE = "https://sandbox.zenodo.org/api/deposit/depositions"
    
    #https://zenodo.org/api/deposit/depositions?access_token=ZENODO_TOKEN
    
    with open(CLIENT_SECRETS_FILE, 'r') as fid:
        ZENODO_TOKEN= '?access_token=' + fid.read()
    
    
    r = requests.get(ZENODO_SCOPE + ZENODO_TOKEN)
    if r.status_code != 200:
        print(r.json())


    #%%
    f2copy = results[-111:-108]
    import shutil
    copy_dir = '/Users/ajaver/OneDrive - Imperial College London/Tests/different_animals/single_worm'
    for experiment_id, mask_file, skeletons_file, features_file in f2copy:
        subsampled_file = getSubSampleVidName(mask_file)
        wcon_file = getWCOName(features_file)
        for fname in [mask_file, skeletons_file, features_file, subsampled_file, wcon_file]:
            shutil.copy(fname, copy_dir)
    
    