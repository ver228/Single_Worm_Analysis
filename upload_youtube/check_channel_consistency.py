#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 12:26:16 2017

@author: ajaver
"""
import pandas as pd
import pymysql
import numpy as np
import json
import sys
import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

CLIENT_SECRETS_FILE = "client_secrets.json"

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_SCOPE)

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage)

service =  build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
  


channel_id = 'UCx36wu_Hh0sGvPaCkAMHrMg'
uploads_list_id = 'UUx36wu_Hh0sGvPaCkAMHrMg'
#response = service.channels().list(id=channel_id, part='snippet,contentDetails,statistics').execute()

#https://www.googleapis.com/youtube/v3/search?key={your_key_here}&channelId={channel_id_here}&part=snippet,id&order=date&maxResults=20

#https://www.googleapis.com/youtube/v3/search?key=


# Retrieve the list of videos uploaded to the authenticated user's channel.
playlistitems_list_request = service.playlistItems().list(
        playlistId=uploads_list_id,
        part="snippet",
        maxResults=50
      )

all_responses = []
n_response = 0
while playlistitems_list_request:
    n_response += 1
    print(n_response)
    
    playlistitems_list_response = playlistitems_list_request.execute()
    all_responses.append(playlistitems_list_response)
    
    playlistitems_list_request = service.playlistItems().list_next(
      playlistitems_list_request, playlistitems_list_response
      )

#%%
dd = [[z['snippet'] for z in x['items']] for x in all_responses]
dd = sum(dd, [])

all_data = []
for snippet in dd:
    
    youtube_id = snippet['resourceId']['videoId']
    publishedAt = snippet['publishedAt']
    try:
        dat = snippet['description'].partition('Experiment metadata:')[-1].replace('\n', '')
        base_name = json.loads(dat)['base_name']
    except:
        base_name = ''
    all_data.append((youtube_id, publishedAt, base_name))

df = pd.DataFrame(all_data, columns = ['youtube_id', 'published_timestamp', 'base_name'])
df['published_timestamp'] = pd.to_datetime(df['published_timestamp'])


#%%

old_df = df[df['base_name'] == '']
old_df = old_df[old_df['youtube_id']!='GDe7tE9ZL4c'] #this id is the hardware assembly tutorial

last_date_old = old_df['published_timestamp'].max()
old_videos_ids = old_df['youtube_id'].values

with open('old_videos_ids.txt', 'w') as fid:
    fid.write('\n'.join(old_videos_ids))
#%%
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SCOPE)

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage)

service_w =  build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
#%%

if False:
    gg = old_df.sort_values(by='published_timestamp').iterrows()
    
    for ii, (_, row) in enumerate(gg):
        if row['youtube_id'] == 'GDe7tE9ZL4c':
            continue
        
        if ii < 9996:
            continue
        
        print(ii)
        videos_update_response = service_w.videos().update(
                part='status',
                body=dict(
                    id = row['youtube_id'],
                    status = dict(privacyStatus='unlisted')
                    )
                ).execute()
        
        service_w.playlistItems().insert(
                part = 'snippet',
                body={"snippet" : {
                        "playlistId" : 'PLOlaNAgEz6CqllIgEv09ZUt1EeFg7C31K',
                        "resourceId" : {
                                "kind"  : "youtube#video",
                                "videoId" : row['youtube_id']
                                }
                        }
                    }
                ).execute()
    
#%%

if False:
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()

    sql = '''
    SELECT id, base_name, youtube_id 
    FROM experiments 
    WHERE youtube_id IS NOT NULL
    '''
    cur.execute(sql)
    db_youtube_ids = cur.fetchall()
    db_df = pd.DataFrame(np.array(list(zip(*db_youtube_ids))).T, columns=['id', 'base_name', 'youtube_id'])
    #db_df.to_csv('old_db_youtube_ids.csv')
    
    conn.close()
    
if False:
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    
    new_df = df[df['base_name'] != '']
    for _, row in new_df.iterrows():
        sql = '''
        UPDATE experiments 
        SET youtube_id = "{youtube_id}"
        WHERE base_name = "{base_name}";
        '''.format(base_name=row['base_name'], youtube_id=row['youtube_id'])
        cur.execute(sql)
    conn.close()

#%%
#eq = [(db_equiv[row['base_name']], row['youtube_id']) for _, row in new_df.iterrows()]
#set(db_equiv.values())-set(new_df['youtube_id'])
#len(set(new_df['base_name']) - set(db_equiv.keys()))
#len(set(new_df['youtube_id']) - set(db_equiv.values()))
#%%



