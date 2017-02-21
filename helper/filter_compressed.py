#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:45:43 2017

@author: ajaver
"""



import pymysql
import os


def get_unfinished_in_list(list_path):
    def _get_file_progress(fname):
        sql = '''
        select f.id
        from experiments as e
        join analysis_progress as a on e.id = a.experiment_id
        join exit_flags as f on f.id = a.exit_flag_id
        where original_video = "{}"
        '''.format(fname)
    
        cur.execute(sql)
    
        row = cur.fetchone()
        
        if row is not None:
            return row[0]
        else:
            return -1
    
    with open(list_path) as fid:
        file_list = [x for x in fid.read().split('\n')]
    
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    
    dd = zip(file_list, map(_get_file_progress, file_list))
    unfinished = [fname for fname, flag in dd if flag <= 12]
    return unfinished
    conn.close()

def save_finished_list():
    list_path = '/Users/ajaver/Documents/GitHub/Single_Worm_Analysis/files_lists/vid_on_food_1.txt'
    unfinished = get_unfinished_in_list(list_path)
    with open(list_path.replace('.txt', '_new.txt'), 'w') as fid:
        fid.write('\n'.join(unfinished))

def divide_and_save(file_list, n_div, save_prefix):
    divided_files = [[] for i in range(n_div)]
                
    
    for ii, fname in enumerate(file_list):
        ind = ii % n_div
        divided_files[ind].append(fname)
    
    for ii, f_list in enumerate(divided_files):
        with open('{}_{}.txt'.format(save_prefix, ii+1), 'w') as fid:
            fid.write('\n'.join(f_list))

if __name__ == '__main__':
    
    
    sql = '''
        select f.checkpoint, original_video
        from experiments as e
        join analysis_progress as a on e.id = a.experiment_id
        join exit_flags as f on f.id = a.exit_flag_id
        order by original_video_sizeMB DESC
        '''
    
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    cur.execute(sql)

    rows = cur.fetchall()
    
    files_progress = {}
    
    for checkpoint, file in rows:
        if not checkpoint in files_progress:
            files_progress[checkpoint] = []
        files_progress[checkpoint].append(file)
    
    print({x:len(val) for x,val in files_progress.items()})
    #%%
    #points2save = ['TRAJ_CREATE', 'BLOB_FEATS']
    points2save = ['INT_PROFILE']
    files2save = sum([files_progress[x] for x in points2save], [])
    divide_and_save(files2save, 2, 'intensity')
    
    #%%
#    files2save = files_progress['CONTOUR_ORIENT']
#    with open('unfinished.txt', 'w') as fid:
#        fid.write('\n'.join(files2save))
    
    
    