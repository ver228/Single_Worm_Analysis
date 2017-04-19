import os
import pymysql

MOVIES_LIST_F = os.path.realpath(os.path.join('..', '..', 'files_lists', 'single_worm.txt'))
ORIGINAL_VIDEO_ROOT_DIR = 'Volumes/behavgenom_archive$/single_worm/original_videos/'


if __name__ == '__main__':
    with open(MOVIES_LIST_F, 'r') as fid:
        fnames = fid.read()
        fnames = fnames.split('\n')
    base_names = [os.path.basename(x).replace('.avi', '') for x in fnames if x]
    
    bn_dict = {x:y for (x,y) in zip(base_names, fnames)}
    
    conn = pymysql.connect(host='localhost', db = 'single_worm_db')
    cur = conn.cursor()
    sql = '''
    SELECT base_name
    FROM experiments
    '''
    cur.execute(sql)
    results = cur.fetchall()
    
    valid_bn = [x[0] for x in results]
    
    
    sql_cmd = '''
    UPDATE experiments SET original_video="{1}" WHERE base_name="{0}";
    '''
    
    for bn in valid_bn:
        sql = sql_cmd.format(bn, bn_dict[bn])
        cur.execute(sql)
    conn.commit()
        
    
    