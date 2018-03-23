#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:46:03 2017

@author: ajaver
"""
import time
import pymysql
import os
import requests
import json
import zipfile
from tierpsy.analysis.wcon_export.exportWCON import readMetaData

WEBPAGE_INFO= '''<blockquote>
<p>This experiment is part of the&nbsp;<em>C.elegans behavioural database</em>. For more information and the complete collection of experiments visit&nbsp;http://movement.openworm.org</p>
</blockquote>\n
'''
def printItems(dictObj, indent=0):
    dd = ''
    dd += '  '*indent + '<ul>\n'
    for k,v in dictObj.items():
        
        
        if isinstance(v, dict):
            v_str = printItems(v, indent+1)
        #elif isinstance(v, list):
        #    v_str = ''
        #    for vl in v:
        #        v_str += '{}{}\n'.format('  '*(indent+1), printItems(vl, indent+2)) 
        else:
            v_str = v
        
        if v_str:
            dd += '{}<li><b>{}</b> : {}</li>\n'.format('  '*indent, k, v_str) 
    dd += '  '*indent + '</ul>\n'
    return dd

def print_errors(r, fname):
    print('{}\n{} : {}'.format(fname, r.status_code, r.reason))         
    try:
        q = r.json()
        if 'message' in q:
            print(q['message'])
        
    except:
        pass

#%%
if __name__ == '__main__':
    use_sandbox = False
    backup_file = 'zenodo_ids.txt'
    CLIENT_SECRETS_FILE = "client_secrets.txt"
    
    skip_masks = False
    
    #creators???
    creators_dlft = \
    [{'name': 'Javer, Avelino'},
     {'name': 'Currie, Michael'},
     {'name': 'Hokanson, Jim'},
     {'name': 'Lee, Chee Wai'},
     {'name': 'Li, Kezhi'},
     {'name': 'Yemini, Eviatar'},
     {'name': 'Grundy, Laura J'},
     {'name': 'Li, Chris'},
     {'name': 'Ch’ng, Quee-Lim'},
     {'name': 'Schafer, William R'},
     {'name': 'Kerr, Rex'},
     {'name': 'Brown, André EX'}]
    
    creators_available = {
            "Celine N. Martineau, Bora Baskaner" :
            [{'name': 'Martineau, Celine N.'},
              {'name' : 'Nollen, Ellen A. A.'}
             ]
            }
    
    headers = {"Content-Type": "application/json"}
    #%%
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    sql = '''
    SELECT id, extension 
    FROM file_types 
    '''
    cur.execute(sql)
    ext2upload = cur.fetchall()
    
    #%%
    sql = '''
    SELECT ev.*, youtube_id, z.zenodo_id
    FROM experiments_valid as ev
    JOIN experiments AS e ON ev.id = e.id
    LEFT JOIN zenodo_files AS z ON z.experiment_id = e.id
    WHERE youtube_id IS NOT NULL
    '''
    
    cur.execute(sql)
    missing_depositions = cur.fetchall()
    missing_depositions = [x for x in missing_depositions if x['zenodo_id'] is None]
    #%%
    sql = '''
    SELECT ev.*, youtube_id, zenodo_id 
    FROM (
    SELECT experiment_id, zenodo_id, count(*) as z_counts 
    FROM zenodo_files 
    GROUP BY experiment_id, zenodo_id
    ) as Z 
    JOIN experiments_valid as ev ON Z.experiment_id = ev.id
    JOIN experiments AS e ON ev.id = e.id
    WHERE z_counts < 3;
    '''
    cur.execute(sql)
    incomplete_depositions = cur.fetchall()
    
    #%%
    with open(CLIENT_SECRETS_FILE, 'r') as fid:
        ZENODO_TOKENS = [x for x in fid.read().split('\n') if x]
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
    
    
    f_data_l = missing_depositions
    #import random
    #f_data_l = random.sample(f_data, 1)
    
    for irow, row in enumerate(f_data_l):
        print(irow+1, len(f_data_l))
        
        features_file = os.path.join(row['results_dir'], row['base_name'] + '_features.hdf5')
        metadata_dict = readMetaData(features_file)
        
        #remove unnessesary fields if they are present
        for ss in ['original_video_name', 'tracker']:
            if ss in metadata_dict:
                del metadata_dict[ss]
        
        #convert the protocol field into a string
        metadata_dict['protocol'] = '. '.join([x[0].upper() + x[1:] for x in metadata_dict['protocol']])
        
        
        metadata_dict['total time (s)'] = row['total_time']
        metadata_dict['frames per second'] = row['fps']
        metadata_dict['video micrometers per pixel'] = row['microns_per_pixel']
        metadata_dict['number of segmented skeletons'] = row['n_segmented_skeletons']
        
        if 'youtube_id' in row:
            metadata_dict['preview link'] = 'https://www.youtube.com/watch?v={}'.format(row['youtube_id'])
            metadata_dict.move_to_end('preview link', last=False)
            #link_str = '<a href="{}">{}</a>\n'.format(dd, dd)
            #zenodo does not support embeded videos (or links)
            #embeded_str = '<p><iframe width="420" height="315"' \
            #'src="https://www.youtube.com/embed/{}?autoplay=1&loop=1">'.format(row['youtube_id'])
            #metadata_dict['preview link'] = link_str + embeded_str
        
        title_str = '{} {} | {}'.format(metadata_dict['strain'], metadata_dict['strain_description'], metadata_dict['timestamp'])
        description_str = WEBPAGE_INFO + printItems(metadata_dict)
        
        while True:  
            try:
                if row['zenodo_id'] is not None:
                    deposition_id = row['zenodo_id']
                    #%%
                    sql = '''
                    SELECT id, extension
                    FROM file_types
                    WHERE id NOT IN (
                    SELECT file_type_id 
                    FROM zenodo_files WHERE 
                    zenodo_id = {})
                    '''.format(row['zenodo_id'])
                    
                    cur.execute(sql)
                    remaining_ext = cur.fetchall()
                    
                else:
                    remaining_ext = ext2upload
                    
                    r = requests.post(ZENODO_URL,
                                   params={'access_token': ACCESS_TOKEN}, 
                                   json={},
                                   headers=headers)
                    deposition_id = r.json()['id']
                    if r.status_code >= 400:
                        print_errors(r, row['base_name'])
                        
                    else:
                        with open(backup_file, 'a') as file:
                            file.write('{}\t{}\n'.format(row['id'], row['base_name'], deposition_id))
        
        
                if row['experimenter'] in creators_available:
                    creators_str = creators_available[row['experimenter']]
                else:
                    creators_str = creators_dlft
                    
        
                #add header
                data = {
                        'metadata': {
                         'title': title_str,
                         'upload_type': 'dataset',
                         'description': description_str,
                         'creators': creators_str,
                         'access_right' : 'open',
                         'license' : "CC-BY-4.0",
                         'communities' : [{'identifier' : 'open-worm-movement-database'}]
                    }
                }
                r = requests.put('{}/{}'.format(ZENODO_URL, deposition_id),
                          params={'access_token': ACCESS_TOKEN}, data=json.dumps(data),
                          headers=headers)
                if r.status_code  < 400:
                    break
                else:
                    print_errors(r, row['base_name'])
                    raise ValueError('There was something wrong with the metadata')
            
            except :
                print(r.status_code)
                print('Error. Trying again in a minute')
                time.sleep(1)
                
        #%%

        while True:
            try:
                r = requests.get('https://zenodo.org/api/deposit/depositions/{}'.format(deposition_id),
                         params={'access_token': ACCESS_TOKEN}, json={}, headers=headers)
                bucket_url = r.json()['links']['bucket']
                break
            except:
                print('Error. Trying again in a minute')
                time.sleep(1)
                
        #%%
        for ft in remaining_ext:
            while True:
                try:
                    fname = row['base_name'] + ft['extension']
                    print(fname)
                    fullpath = os.path.join(row['results_dir'], fname)
                    
                    if 'wcon' in ft['extension']:
                        with zipfile.ZipFile(fullpath) as zf:
                            ret = zf.testzip()
                        if not ret is None:
                            print('corrupt file')
                            raise
                    #import pdb
                    #pdb.set_trace()
                    #%%
#                    with open(fullpath, 'rb') as fp:
#                        url = 'https://zenodo.org/api/deposit/depositions/{}/files?access_token={}'.format(deposition_id, ACCESS_TOKEN)
#                        data = {'filename': os.path.basename(fullpath)}
#                        files = {'file': fp}
#                        file_r = requests.post(url, data=data, files=files)
                    #%%
                    
                    headers_upload = {"Accept":"application/json",
                                    "Authorization":"Bearer %s" % ACCESS_TOKEN,
                                    "Content-Type":"application/octet-stream"
                                    }
                    
                    ff = fname.replace('#', '_')
                    
                    with open(fullpath, 'rb') as fp:
                         file_r = requests.put(bucket_url + '/' + ff,
                                     data = fp,
                                     headers = headers_upload
                                     )
                         
                         
                         
                    #%%
                    break
                except:
                    print('Error. Trying again in a minute')
                    time.sleep(1)
            #OLD REST API               
            #data = {'filename': fname}
            #files = {'file': open(fullpath, 'rb')}
            #r = requests.post(ZENODO_URL + '/%s/files' % deposition_id,
            #               params={'access_token': ACCESS_TOKEN}, data=data,
            #               files=files)


            if r.status_code  >= 400:
                print_errors(file_r, row['base_name'])
            else:
                try:
                    #%%
                    q = file_r.json()
                    sql = '''
                    INSERT INTO zenodo_files (experiment_id, file_id, zenodo_id, filename, filesize, checksum, file_type_id) 
                    VALUES({}, "{}", {}, "{}", {}, "{}", {});
                    '''.format(int(row['id']), q['version_id'], deposition_id, q['key'], q['size'], q['checksum'], ft['id'])
                    cur.execute(sql)
                    conn.commit()
                except:
                    continue
        
                #%%
    conn.close()

        
        
        
        