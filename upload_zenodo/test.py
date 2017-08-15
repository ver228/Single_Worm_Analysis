#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:46:03 2017

@author: ajaver
"""
import pymysql
import os
import sys
import requests
sys.path.append('../2_create_database')
from helper.db_info import db_row2dict

ext2upload = ['.hdf5',
              '_skeletons.hdf5', 
             '_features.hdf5',
             '_subsample.avi', 
             '.wcon.zip'
             ]

if __name__ == '__main__':
    CLIENT_SECRETS_FILE = "client_secrets.txt"
    with open(CLIENT_SECRETS_FILE, 'r') as fid:
        ZENODO_TOKENS = [x for x in fid.read().split('\n') if x]
    
    use_sandbox = True
    
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    sql = '''
    SELECT *
    FROM experiments_valid
    '''
    
    cur.execute(sql)
    f_data = cur.fetchall()
    
    if use_sandbox:
        ZENODO_URL = "https://sandbox.zenodo.org/api/deposit/depositions"
        ACCESS_TOKEN = ZENODO_TOKENS[0]
    else:
        ZENODO_URL = "https://zenodo.org/api/deposit/depositions"
        ACCESS_TOKEN = ZENODO_TOKENS[1]
    
    r = requests.get(ZENODO_URL, params={'access_token': ACCESS_TOKEN})
    if r.status_code != 200:
        msg = r.json()
        raise ValueError('{}: {}'.format(msg['status'], msg['message']))
    
    
    row = f_data[0]
    metadata = db_row2dict(row)
 
    files = []
    
#    headers = {"Content-Type": "application/json"}
#    r = requests.post(ZENODO_URL,
#                   params={'access_token': ACCESS_TOKEN}, 
#                   json={},
#                   headers=headers)
#    deposition_id = r.json()['id']
    
    deposition_id = 78698
    
    for ext in ext2upload:
        
        fname = row['base_name'] + ext
        fullpath = os.path.join(row['results_dir'], fname)
        data = {'filename': fname}
        files = {'file': open(fullpath, 'rb')}
        
        print(fname)
        r = requests.post(ZENODO_URL + '/%s/files' % deposition_id,
                       params={'access_token': ACCESS_TOKEN}, data=data,
                       files=files)

        print(r.json())
    
    conn.close()

#
# headers = {"Content-Type": "application/json"}
#    r = requests.post('https://zenodo.org/api/deposit/depositions',
#                      params={'access_token': ACCESS_TOKEN}, json={},
#                      headers=headers)
#
#>>> r.status_code
#     data = {
#...     'metadata': {
#...         'title': 'My first upload',
#...         'upload_type': 'poster',
#...         'description': 'This is my first upload',
#...         'creators': [{'name': 'Doe, John',
#...                       'affiliation': 'Zenodo'}]
#...     }
#... }
#
#r = requests.put('https://zenodo.org/api/deposit/depositions/%s' % deposition_id,
#...                  params={'access_token': ACCESS_TOKEN}, data=json.dumps(data),
#...                  headers=headers)
#>>> r.status_code
    
   
    
    

