#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:45:43 2017

@author: ajaver
"""



import pymysql
import os



def get_all(is_swimming = False):
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    
    sql_liquid = '''
    select original_video 
    from experiments
    where arena like '%liquid%' 
    order by original_video_sizeMB DESC'''
    
    
    sql_agar = '''
    select original_video 
    from experiments
    where arena not like '%liquid%'
    order by original_video_sizeMB DESC'''
    
    if is_swimming:
        cur.execute(sql_liquid)
    else:
        cur.execute(sql_agar)
    
    file_list = cur.fetchall()
    file_list = [x for x, in file_list] #flatten




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

def _get_mask_name(base_name, results_dir):
    return os.path.join(results_dir, base_name + '.hdf5')

if __name__ == '__main__':
#    sql = '''
#        select results_dir, base_name
#        from experiments as e
#        order by original_video_sizeMB DESC
#        '''
#    
#    conn = pymysql.connect(host='localhost', database='single_worm_db')
#    cur = conn.cursor()
#    cur.execute(sql)
#    rows = cur.fetchall()
#    
#        
#    with open('all_files', 'w') as fid:
#        all_masks = [_get_mask_name(*x) for x in rows]
#        fid.write('\n'.join(all_masks))
#%%    
    sql = '''
        select f.id, f.name, original_video, results_dir, base_name
        from experiments as e
        join exit_flags as f on f.id = e.exit_flag_id
        join arenas as a on arena_id = a.id
        where a.name not like '%liquid%'
        order by original_video_sizeMB DESC
        '''
    
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    
    files_progress = {}
    for exit_flag_id, checkpoint, original_video, results_dir, base_name in rows:
        if not checkpoint in files_progress:
            files_progress[checkpoint] = []
        
        if exit_flag_id > 2:
            file = _get_mask_name(base_name, results_dir)
        else:
            file = original_video
        files_progress[checkpoint].append(file)
    
    print({x:len(val) for x,val in files_progress.items()})
    
    ignore_fields = ['INVALID_VIDEO', 'FAIL_STAGE_ALIGMENT', 'END', 'UNKNOWN_CONTOUR_ORIENT']
    points2save = [x for x in files_progress.keys() if not x in ignore_fields]
    points2save = ['CONTOUR_ORIENT']
    files2save = sum([files_progress[x] for x in points2save], [])
    
    divide_and_save(files2save, 1, 'cnt_orient')
    
