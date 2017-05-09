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
from tierpsy.helper.misc import RESERVED_EXT

valid_ext = RESERVED_EXT.copy()
valid_ext.append('.hdf5')

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
    #I NEED TO ADD SOMETHING TO DEAL WITH FINISH UNFINISHED HERE
    
    exiting_files = glob.glob(os.path.join(dir_root, '**', '*.hdf5'), recursive=True)
    exiting_files = [x for x in exiting_files if not any(x.endswith(rext) for rext in RESERVED_EXT)]
    for fullname in exiting_files:
        dname, fname = os.path.split(fullname)
        base_name = fname.replace('.hdf5', '')
        
        dpart = get_dir_from_base(base_name)
        dname_correct = os.path.join(dir_root, dpart)
        
        
        if os.path.abspath(dname_correct) != os.path.abspath(dname):
            all_files = [os.path.join(dname, base_name + rext) for rext in  valid_ext]
            files2move = [x for x in all_files if os.path.exists(x)]
            for ff in files2move:
                shutil.move(ff, dname_correct)

if __name__ == '__main__':
    dir_root_r = '/Volumes/behavgenom_archive$/single_worm/'

    conn = pymysql.connect(host='localhost')
    cur = conn.cursor()
    
    cur.execute('USE `single_worm_db`')
    
    sql = '''
    SELECT e.id, results_dir, base_name, original_video, f.name
    FROM experiments AS e
    JOIN exit_flags AS f ON f.id = exit_flag_id
    '''
    cur.execute(sql)
    results = cur.fetchall()
    
    
    tot = len(results)
    for ii, (exp_id, results_dir, base_name, original_video, exit_flag) in enumerate(results):
        #correct from the original schaffer path
        original_video = _correct_from_old(original_video)
        files2move = get_files_old(original_video) 
        
        if exit_flag != 'END':
            dst_root = os.path.join(dir_root_r, 'unfinished')
        else:
            dst_root = os.path.join(dir_root_r, 'finished')
        
        dpart = get_dir_from_base(base_name)
        
        dst_dir = os.path.join(dst_root, dpart)
        
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        
        def _get_files2move(dname):
            files2move = [os.path.join(dname, base_name + rext) for rext in  valid_ext]
            files2move = [x for x in files2move if os.path.exists(x)]
            return files2move
            
        
        if len(files2move) == 0:
            files2move = _get_files2move(results_dir)
            if not 'unfinished' in results_dir:
                d = os.path.sep
                old_dir = results_dir.replace(d + 'finished' + d, d + 'unfinished' + d)
                files2move += _get_files2move(old_dir)
                
                
        
        files_moved = 0
        for fname in files2move:
            if os.path.exists(fname):
                dst_file = os.path.abspath(os.path.join(dst_dir, os.path.basename(fname)))
                if dst_file != fname:
                    shutil.move(fname, dst_dir)
                    files_moved += 1
        
        if files_moved > 0:
            sql = '''
            UPDATE experiments
            SET results_dir="{}"
            WHERE id = {}
            '''.format(dst_dir, exp_id)
            cur.execute(sql)
            conn.commit()
        
        print('{} of {}: {} "{}"'.format(ii+1, tot, files_moved, base_name))

        