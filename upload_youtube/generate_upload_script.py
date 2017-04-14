import pymysql
import os
import json
import time
from upload_video import get_authenticated_service, resumable_upload
from apiclient.http import MediaFileUpload


from tierpsy.analysis.vid_subsample.createSampleVideo import createSampleVideo
from tierpsy.analysis.wcon_export.exportWCON import getWCONMetaData

from googleapiclient.errors import ResumableUploadError

    
def resample_and_upload(masked_video, 
                        speed_up, 
                        db_cursor,
                        skip_invalid = False,
                        backup_file='youtube_ids.txt'):
    
    WEBPAGE_INFO="For more information and the complete collection of experiments visit the C.elegans behavioural database - http://movement.openworm.org\n"
    LOCAL_ROOT_DIR = "/Volumes/behavgenom_archive$/single_worm/thecus/"
    TMP_DIR =  os.path.realpath(os.path.expanduser(os.path.join('~', 'Tmp')))
    
    metadata_dict = getWCONMetaData(masked_video, provenance_step='COMPRESS')
    
    if not "original_video_name" in metadata_dict:
        if skip_invalid:
            return None
        else:
            raise(KeyError('Wrong /experiment_info .'))
    
    #i do not want to specify the full path
    metadata_dict["original_video_name"] = metadata_dict["original_video_name"].replace(LOCAL_ROOT_DIR, '.')
    metadata_str = json.dumps(metadata_dict, allow_nan=False, indent=0)
    
    description = WEBPAGE_INFO + '\n\nExperiment metadata:\n'+ metadata_str
    title_str = '{} {} | {}'.format(metadata_dict['strain'], metadata_dict['genotype'], metadata_dict['timestamp'])
    tmp_file = os.path.join(TMP_DIR, base_name + '.avi')
    if speed_up != 1:
        title_str = title_str + ' (speed up {}x)'.format(speed_up)
        tmp_file = tmp_file.replace('.avi', '_{}x.avi'.format(speed_up))
        description = 'This video is {}x speed up version of the original.'.format(speed_up) + description
    
    print(title_str)
    createSampleVideo(masked_video, tmp_file, time_factor = speed_up, 
                     size_factor = 1, codec='MPEG')
    
    body=dict(
    snippet = dict(title=title_str, description=description, categoryId=28),
    status=dict(privacyStatus=youtube_privacy_status)
    )
    
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
            
            with open(backup_file, 'a') as file:
                file.write('{}\t{}\n'.format(base_name, youtube_id))
            
            sql = INSERT_SQL.format(experiment_id, youtube_id)       
            db_cursor.execute(sql)
            
            
            print('I am waiting for a minute before uploading the next video.')
            time.sleep(60)
            break
        
        except ResumableUploadError:
            min_to_wait = 30
            print('The limit of youtube uploads has been reached. I will try it again in {} minutes.'.format(min_to_wait))
        for n in range(1, min_to_wait+1):
            time.sleep(60)
            print(n, end=' ', flush=True)
        print()
    
    os.remove(tmp_file)
    return youtube_id

def _correct_from_list():
    with open('youtube_ids.txt', 'r+') as file:
        data = file.read()
    
    for bn, yid in [x.split('\t') for x in data.split('\n') if x]:
        sql = '''
        SELECT id
        FROM experiments
        WHERE base_name = "{}"
        '''.format(bn)
        
        cur.execute(sql)
        
        eid, = cur.fetchone()
        sql = INSERT_SQL.format(eid, yid)       
        cur.execute(sql)
        conn.commit()


INSERT_SQL = '''INSERT INTO external_links (experiment_id, youtube_id) VALUES ({0},"{1}")
  ON DUPLICATE KEY UPDATE youtube_id="{1}";'''


if __name__ == '__main__':
    skip_invalid = True 
    speed_up = 8
    youtube_privacy_status='public'#'private'
    
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    
    ori_vid_sql = '''
    SELECT id, base_name, results_dir
    FROM experiments
    WHERE exit_flag_id > 1
    AND id NOT IN (
    SELECT experiment_id
    FROM external_links
    WHERE youtube_id IS NOT NULL
    )
    ORDER BY id'''
    cur.execute(ori_vid_sql)
    results = cur.fetchall()
    
    
    
    youtube_client = get_authenticated_service()
    
    #results = results[10212:10213]
    for ii, (experiment_id, base_name, results_dir) in enumerate(results):
        masked_video = os.path.join(results_dir, base_name + '.hdf5')
        
        youtube_id = resample_and_upload(masked_video, speed_up, cur, skip_invalid)
        print('{} of {} %%%%%%%%%%%%%%%%%%%%%%%%%%%'.format(ii+1, len(results)))
        conn.commit()

        
