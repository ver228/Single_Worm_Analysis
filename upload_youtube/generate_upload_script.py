import pymysql
import os
import json
from upload_video import get_authenticated_service, resumable_upload
from apiclient.http import MediaFileUpload


from MWTracker.analysis.vid_subsample.createSampleVideo import createSampleVideo
from MWTracker.analysis.wcon_export.exportWCON import getWCONMetaData

    
def resample_and_upload(masked_video, speed_up):
    WEBPAGE_INFO="For more information and the complete collection of experiments visit the C.elegans behavioural database - http://movement.openworm.org\n"
    LOCAL_ROOT_DIR = "/Volumes/behavgenom_archive$/single_worm/thecus/"
    TMP_DIR =  os.path.realpath(os.path.expanduser(os.path.join('~', 'Tmp')))
    
    metadata_dict = getWCONMetaData(masked_video, provenance_step='COMPRESS')
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
    
    response = resumable_upload(insert_request)
    os.remove(tmp_file)
    
    return response


if __name__ == '__main__':
    
    speed_up = 8
    youtube_privacy_status='private'
    
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    
    ori_vid_sql = '''
    SELECT e.id, e.base_name, p.mask_file 
    FROM progress_analysis AS p 
    JOIN experiments AS e ON p.experiment_id = e.id
    WHERE exit_flag_id > 1
    ORDER BY experiment_id'''
    cur.execute(ori_vid_sql)
    results = cur.fetchall()
    
    
    youtube_client = get_authenticated_service()
    
    results = results[1305:1306]
    for ii, (experiment_id, base_name, masked_video) in enumerate(results):
        response = resample_and_upload(masked_video, speed_up)
        #%%
        print('{} of {} %%%%%%%%%%%%%%%%%%%%%%%%%%%'.format(ii+1, len(results)))
        