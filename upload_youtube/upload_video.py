import pymysql
import os
import json
import time
import datetime
from random import shuffle
from upload_video_helper import get_authenticated_service, resumable_upload
from apiclient.http import MediaFileUpload


from tierpsy.analysis.vid_subsample.createSampleVideo import createSampleVideo
from tierpsy.analysis.wcon_export.exportWCON import readMetaData


DATABASE_NAME = 'single_worm_db'
INSERT_SQL = '''UPDATE experiments SET youtube_id="{1}" WHERE base_name="{0}";'''
youtube_client = get_authenticated_service()    

snippet_tags = ['c.elegans', 'c.elegans behavior', 'c.elegans behaviour', 'computer vision', 'molecular biology', 'neuroscience', 'science', 'worm behavior', 'worm behaviour']

def resample_and_upload(base_name, 
                        results_dir,
                        speed_up,
                        skip_invalid = False,
                        backup_file='youtube_ids.txt'):
    
    masked_video = os.path.join(results_dir, base_name + '.hdf5')
    
    WEBPAGE_INFO="For more information and the complete collection of experiments visit the C.elegans behavioural database - http://movement.openworm.org\n"
    LOCAL_ROOT_DIR = "/Volumes/behavgenom_archive$/single_worm/thecus/"
    TMP_DIR =  os.path.realpath(os.path.expanduser(os.path.join('~', 'Tmp')))
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    metadata_dict = readMetaData(masked_video, provenance_step='COMPRESS')
    
    #if not "original_video_name" in metadata_dict:
    #    if skip_invalid:
    #        return None
    #    else:
    #        raise(KeyError('Wrong /experiment_info .'))
    print(metadata_dict)

    #i do not want to specify the full path
    if "original_video_name" in metadata_dict:
        metadata_dict["original_video_name"] = metadata_dict["original_video_name"].replace(LOCAL_ROOT_DIR, '.')
    metadata_str = json.dumps(metadata_dict, allow_nan=False, indent=0)
    
    description = WEBPAGE_INFO + '\n\nExperiment metadata:\n'+ metadata_str
    
    postfix = ''
    if 'days_of_adulthood' in metadata_dict:
        if metadata_dict["stage"] == 'adult':
            postfix = ' | {} days'.format(metadata_dict['days_of_adulthood'])
        else:
            postfix = ' | {}'.format(metadata_dict["stage"])
    
    title_str = '{} {}{} | {}'.format(metadata_dict['strain'], metadata_dict['strain_description'], postfix, metadata_dict['timestamp'])
    
    if len(title_str) > 87:
        #Likely to excede the title limit. I try to use a shorter name.
        d = metadata_dict['strain_description'].replace(' ', '')
        t = metadata_dict['timestamp'][:10] #I am assuming the date is in the format YYYY-MM-DD
        p = postfix.replace(' ', '')
        title_str = '{} {}{} | {}'.format(metadata_dict['strain'], d,  p, t)

    tmp_file = os.path.join(TMP_DIR, base_name + '.avi')
    
    
    
    
    if speed_up != 1:
        title_str = title_str + ' (speed up {}x)'.format(speed_up)
        tmp_file = tmp_file.replace('.avi', '_{}x.avi'.format(speed_up))
        description = 'This video is {}x speed up version of the original.'.format(speed_up) + description
    
    print(title_str)
    
    createSampleVideo(masked_video, 
                      tmp_file, 
                      time_factor = speed_up, 
                      skip_factor=0.75,
                      size_factor = 1, 
                      codec='MPEG',
                      shift_bgnd = True)
    #%%
    
    body=dict(
    snippet = dict(title=title_str, 
                   description=description, 
                   categoryId=28,
                   tags = snippet_tags
                   ),
    status=dict(privacyStatus=youtube_privacy_status)
    )
    
    print(body)

    insert_request = youtube_client.videos().insert(
    part=",".join(body.keys()),
    body=body,
    media_body=MediaFileUpload(tmp_file, chunksize=-1, resumable=True),
    notifySubscribers = False
    )
    
    while 1:
        try:
            response = resumable_upload(insert_request)
            youtube_id = response['id']
            # print('I am waiting for a few seconds before uploading the next video.')
            # time.sleep(3)
            break
        
        except Exception as e:
            print(e)
            if not "The user has exceeded the number of videos they may upload." in e.content.decode("utf-8"):
                return
            #print('I will wait a few seconds before trying again.')
            #time.sleep(60)
            min_to_wait = 60
            print('The limit of youtube uploads has been reached. I will try it again in {} minutes.'.format(min_to_wait))
        for n in range(1, min_to_wait+1):
            time.sleep(60)
            print(n, end=' ', flush=True)

    with open(backup_file, 'a') as file:
        file.write('{}\t{}\n'.format(base_name, youtube_id))
    
    conn = pymysql.connect(host='localhost', database=DATABASE_NAME)
    cur = conn.cursor()
    sql = INSERT_SQL.format(base_name, youtube_id)       
    cur.execute(sql)
    conn.commit()
    conn.close()
    
    os.remove(tmp_file)
    return youtube_id

def _correct_from_list():
    from collections import Counter

    with open('youtube_ids.txt', 'r+') as file:
        data = file.read()
    data = [x.split('\t') for x in data.split('\n') if x]
    
    dd = Counter([x[0] for x in data])
    duplicated_vals = [x for x, val in dd.items() if val != 1]
    if len(duplicated_vals)!= 0:
        raise ValueError('There are duplicated basenames {}'.format(duplicated_vals))

    #check that all the 
    assert len(set(x[0] for x in data)) == len(data)
    
    conn = pymysql.connect(host='localhost', database=DATABASE_NAME)
    cur = conn.cursor()
    for bn, yid in data:
        sql = INSERT_SQL.format(bn, yid)
        
        cur.execute(sql)
    conn.commit()

if __name__ == '__main__':
    #_correct_from_list()
    skip_invalid = True 
    speed_up = 8
    youtube_privacy_status='public'#'private'
    
    conn = pymysql.connect(host='localhost', database=DATABASE_NAME)
    cur = conn.cursor()
    
    
    ori_vid_sql = '''
    SELECT e.id, e.base_name, e.results_dir
    FROM experiments_valid AS ev
    JOIN experiments AS e ON e.id = ev.id
    WHERE youtube_id IS NULL
    ORDER BY ev.mask_file_sizeMB DESC
    '''
    
    
    cur.execute(ori_vid_sql)
    results = cur.fetchall()
    conn.close()


    results = list(results)
    shuffle(results)
    
    print(len(results))
    
    for ii, (experiment_id, base_name, results_dir) in enumerate(results):
        print('{} of {} %%%%%% {}'.format(ii+1, len(results), datetime.datetime.now()))
        youtube_id = resample_and_upload(base_name, results_dir, speed_up, skip_invalid)
    
    