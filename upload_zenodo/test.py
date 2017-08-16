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
import json
from tierpsy.analysis.wcon_export.exportWCON import getWCONMetaData

sys.path.append('../2_create_database')
from helper.db_info import db_row2dict

ext2upload = ['.hdf5', 
             '_features.hdf5',
             '_subsample.avi', 
             '.wcon.zip'
             ]

def printItems(dictObj, indent):
    dd = ''
    dd += '  '*indent + '<ul>\n'
    for k,v in dictObj.items():
        
        
        if isinstance(v, dict):
            v_str = printItems(v, indent+1)
            
        elif isinstance(v, list):
            v_str = [x[0].upper() + x[1:] for x in v]
            v_str = '. '.join(v_str)
        else:
            v_str = v
            
        dd += '{}<li><b>{}</b> : {}</li>'.format('  '*indent, k, v_str) 
    dd += '  '*indent + '</ul>\n'
    return dd


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
    
    
    creators_str = \
    [{'name': 'Javer, Avelino'},
     {'name': 'Currie, Michael'},
     {'name': 'Hokanson, Jim'},
     {'name': 'Lee, Chee Wai'},
     {'name': 'Li, Kezhi'},
     {'name': 'Yemini, Ev'},
     {'name': 'Grundy, Laura J'},
     {'name': 'Li, Chris'},
     {'name': 'Ch’ng, Quee-Lim'},
     {'name': 'Schafer, William R'},
     {'name': 'Kerr, Rex'},
     {'name': 'Brown, André EX'}]
    
    headers = {"Content-Type": "application/json"}
    for irow, row in enumerate(f_data[2:]):
        print(irow, len(f_data)+1)
        metadata = db_row2dict(row)
     
        masked_video = os.path.join(row['results_dir'], row['base_name'] + '.hdf5')
        metadata_dict = getWCONMetaData(masked_video, provenance_step='COMPRESS')
        
        del metadata_dict['original_video_name']
        del metadata_dict['tracker']
        
        metadata_dict['total time (s)'] = row['total_time']
        metadata_dict['frames per second'] = row['fps']
        metadata_dict['number of segmented skeletons'] = row['n_segmented_skeletons']
        
        
        title_str = '{} {} | {}'.format(metadata_dict['strain'], metadata_dict['strain_description'], metadata_dict['timestamp'])
        description_str = printItems(metadata_dict, 0)
        
        print(description_str)
        break
        
        
        r = requests.post(ZENODO_URL,
                       params={'access_token': ACCESS_TOKEN}, 
                       json={},
                       headers=headers)
        deposition_id = r.json()['id']
        
        data = {
                'metadata': {
                 'title': title_str,
                 'upload_type': 'dataset',
                 'description': description_str,
                 'creators': creators_str
            }
        }
        
        r = requests.put('{}/{}'.format(ZENODO_URL, deposition_id),
                  params={'access_token': ACCESS_TOKEN}, data=json.dumps(data),
                  headers=headers)
        
    
       
        for ext in ext2upload:
            fname = row['base_name'] + ext
            fullpath = os.path.join(row['results_dir'], fname)
            data = {'filename': fname}
            files = {'file': open(fullpath, 'rb')}
            
            r = requests.post(ZENODO_URL + '/%s/files' % deposition_id,
                           params={'access_token': ACCESS_TOKEN}, data=data,
                           files=files)
            
            
            print('{}\n{} : {}'.format(fname, r.status_code, r.reason))
            
            try:
                q = r.json()
                if 'message' in q:
                    print(q['message'])
                
            except:
                pass
        break
        
        
    conn.close()

#
# 
#    r = requests.post('https://zenodo.org/api/deposit/depositions',
#                      params={'access_token': ACCESS_TOKEN}, json={},
#                      headers=headers)
#

#
#r = requests.put('https://zenodo.org/api/deposit/depositions/%s' % deposition_id,
#...                  params={'access_token': ACCESS_TOKEN}, data=json.dumps(data),
#...                  headers=headers)
#>>> r.status_code
    
   
    
    

