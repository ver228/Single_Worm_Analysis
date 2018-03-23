#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 17:23:18 2017

@author: ajaver
"""
import pandas as pd
import pymysql
import requests

CLIENT_SECRETS_FILE = "client_secrets.txt"
use_sandbox = False

with open(CLIENT_SECRETS_FILE, 'r') as fid:
    ZENODO_TOKENS = [x for x in fid.read().split('\n') if x]
    if use_sandbox:
        ZENODO_URL = "https://sandbox.zenodo.org/api/deposit/depositions"
        ACCESS_TOKEN = ZENODO_TOKENS[0]
    else:
        ZENODO_URL = "https://zenodo.org/api/deposit/depositions"
        ACCESS_TOKEN = ZENODO_TOKENS[1]

if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    sql = '''
    SELECT *
    FROM zenodo_files
    ORDER BY experiment_id
    '''
    
    sql = '''
    SELECT z.*
    FROM experiments_valid as ev
    JOIN experiments AS e ON ev.id = e.id
    RIGHT JOIN zenodo_files AS z ON z.experiment_id = e.id
    WHERE experimenter = "Celine N. Martineau, Bora Baskaner"
    '''
    
    zenodo_files = pd.read_sql(sql, conn)
    
    for experiment_id, dat in zenodo_files.groupby('experiment_id'):
        print(experiment_id)
        
        if set(dat['file_type_id'].values) != {1,2,3}:
            print(dat)
        else:
            dd = dat['zenodo_id'].unique()
            assert len(dd) == 1
            zenodo_id = dd[0]
            r = requests.post(ZENODO_URL + '/%s/actions/publish' % zenodo_id,
                       params={'access_token': ACCESS_TOKEN})