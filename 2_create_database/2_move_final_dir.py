#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 15:16:55 2017

@author: ajaver
"""
import os
import shutil
import pymysql
from helper.build_dir import get_dir_from_base
import glob
from tierpsy.helper.misc import RESERVED_EXT, get_base_name

def get_files_old(original_video):
    
    mask_file = original_video.replace('thecus', 'MaskedVideos').replace('.avi', '.hdf5')
    subvid_file = mask_file.replace('.hdf5', '_subsample.avi')
    
    skel_file = original_video.replace('thecus', 'Results').replace('.avi', '_skeletons.hdf5')
    feat_file = skel_file.replace('_skeletons.hdf5', '_features.hdf5')
    int_file = skel_file.replace('_skeletons.hdf5', '_intensities.hdf5')

    files2move = (mask_file, subvid_file, skel_file, feat_file, int_file)
    files2move = [x for x in files2move if os.path.exists(x)]
    return files2move

def _correct_from_old(original_video):
    
    #%%
    fparts_filt = [x for x in original_video.split(os.sep) if x!='orignal_videos' and 'single_worm_raw_bkp' not in x]
    new_name = os.sep + os.path.join(*fparts_filt)
     
    return new_name

def correct_wrong_path(dir_root):
    exiting_files = glob.glob(os.path.join(dir_root, '**', '*.hdf5'), recursive=True)
    exiting_files = [x for x in exiting_files if not any(x.endswith(rext) for rext in RESERVED_EXT)]
    for fullname in exiting_files:
        dname, fname = os.path.split(fullname)
        base_name = fname.replace('.hdf5', '')
        
        dpart = get_dir_from_base(base_name)
        dname_correct = os.path.join(dir_root, dpart)
        
        
        if os.path.abspath(dname_correct) != os.path.abspath(dname):
            all_files = [os.path.join(dname, base_name + rext) for rext in  RESERVED_EXT]
            files2move = [x for x in all_files if os.path.exists(x)]
            for ff in files2move:
                shutil.move(ff, dname_correct)

if __name__ == '__main__':
    dir_root = '/Volumes/behavgenom_archive$/single_worm/unfinished'

    conn = pymysql.connect(host='localhost')
    cur = conn.cursor()
    
    cur.execute('USE `single_worm_db`')
    
    sql = '''
    SELECT id, base_name, original_video
    FROM experiments_full
    '''
    cur.execute(sql)
    results = cur.fetchall()
    
    
    tot = len(results)
    for ii, (exp_id, base_name, original_video) in enumerate(results):
        original_video = _correct_from_old(original_video)
        
        
        dpart = get_dir_from_base(base_name)
        dname = os.path.join(dir_root, dpart)
        
        if not os.path.exists(dname):
            os.makedirs(dname)
        
        files2move = get_files_old(original_video)
        for fname in get_files_old(original_video):
            if os.path.exists(fname):
                shutil.move(fname, dname)
        
        sql = '''
        UPDATE experiments
        SET results_dir="{}"
        WHERE id = {}
        '''.format(dname, exp_id)
        cur.execute(sql)
        conn.commit()
        
        print('{} of {} : {} "{}"'.format(ii+1, tot, len(files2move), base_name))
        
        