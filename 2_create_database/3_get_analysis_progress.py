# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:17:35 2016

@author: ajaver
"""

import os
import pymysql.cursors
import multiprocessing as mp

from tierpsy.processing.AnalysisPoints import AnalysisPoints
from tierpsy.analysis.stage_aligment.alignStageMotion import isGoodStageAligment
from tierpsy.analysis.contour_orient.correctVentralDorsal import isBadVentralOrient, switchCntSingleWorm, read_ventral_side
from tierpsy.analysis.compress_add_data.getAdditionalData import hasAdditionalFiles
from tierpsy.analysis.compress.processVideo import isGoodVideo

from tierpsy.helper.misc import TimeCounter

from tierpsy import DFLT_PARAMS_PATH
ON_FOOD_JSON = os.path.join(DFLT_PARAMS_PATH, 'single_worm_on_food.json')

from helper.db_info import add_extra_info

def get_points2check():
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    cur.execute('''
    SELECT id, name
    FROM exit_flags
    ORDER BY id
    ''')
    result = cur.fetchall()  
    
    cur.close()
    conn.close()


    points2check = [x[1] for x in result if x[0]<100]
    name2index = {x[1]:x[0] for x in result}
    return points2check, name2index


POINTS2CHECK, NAME2INDEX = get_points2check()
INDEX2NAME = {y:x for x,y in NAME2INDEX.items()}
POINTS2CHECK_M =  [x for x in POINTS2CHECK if x not in ['COMPRESS', 'COMPRESS_ADD_DATA']]
    
#%%
def get_last_finished(ap_obj, cur, points2check):
    def _get_flag_name(_ap_obj):
        
        points2check_m = points2check.copy()
        points2check_m.remove('END')
        unfinished = _ap_obj.getUnfinishedPoints(points2check_m)
        if not unfinished:
            return 'END'
        else:
            if not 'STAGE_ALIGMENT' in unfinished:
                if not isGoodStageAligment(_ap_obj.file_names['skeletons']):
                    return 'FAIL_STAGE_ALIGMENT'
            
            if not 'CONTOUR_ORIENT' in unfinished:
                #i try to switch here. I don't want to deal with this problem in checkpoints
                switchCntSingleWorm(_ap_obj.file_names['skeletons'])
                if read_ventral_side(_ap_obj.file_names['skeletons']) not in ['clockwise', 'anticlockwise'] \
                    or isBadVentralOrient(_ap_obj.file_names['skeletons']):
                    return 'UNKNOWN_CONTOUR_ORIENT'
            
            if 'COMPRESS' in unfinished:
                if not isGoodVideo(_ap_obj.file_names['original_video']):
                    return 'INVALID_VIDEO'
                elif not hasAdditionalFiles(_ap_obj.file_names['original_video']):
                    return 'MISSING_ADD_FILES'
            
            for point in points2check:
                if point in unfinished:
                    return point    
    
    last_point = _get_flag_name(ap_obj)
    
    
    exit_flag_id = NAME2INDEX[last_point]
    return exit_flag_id, last_point

def get_results_files(row):
    results_dir = os.path.realpath(row['results_dir'])
    main_file = os.path.join(results_dir, row['base_name'] + '.hdf5')
    if os.path.exists(main_file):
        masks_dir = results_dir
        points2check = POINTS2CHECK_M
    else:
        main_file = os.path.realpath(row['original_video'])
        video_dir = os.path.dirname(main_file)
        masks_dir = video_dir.replace('thecus', 'MaskedVideos')
        results_dir = video_dir.replace('thecus', 'Results')
        points2check = POINTS2CHECK
    
    return main_file, masks_dir, results_dir, points2check


def get_rows(last_valid='', skip_bad_flags=False):
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    sql = '''
    SELECT e.id, e.original_video, e.base_name, e.results_dir
    FROM experiments AS e
    JOIN exit_flags ON exit_flags.id = e.exit_flag_id
    '''
    if last_valid:
        sql += '''
        WHERE e.exit_flag_id < (SELECT f.id FROM exit_flags as f WHERE f.name="{}")
        '''.format(last_valid)
    
        
    cur.execute(sql)
    all_rows = cur.fetchall()
    
    cur.close()
    return conn, all_rows

if __name__ == '__main__':
    UPDATE_INFO = True
    CHECK_FLAG = False
    last_valid = ''#'FEAT_CREATE' #'WCON_EXPORT'#''# 
    
    conn, all_rows = get_rows(last_valid)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    def _process_row(row):
        main_file, masks_dir, results_dir, points2check = get_results_files(row)
        output = None
        
        if UPDATE_INFO:
            try:
                add_extra_info(cur, row['base_name'], results_dir)
                print('ID:{} info added.'.format(row['id']))
            except:
                pass
            
        if CHECK_FLAG:
            ap_obj = AnalysisPoints(main_file, masks_dir, results_dir, ON_FOOD_JSON)
            exit_flag_id, last_point = get_last_finished(ap_obj, cur, points2check)
            output = (row['id'], exit_flag_id)
            
        
        
        
        return output
    
    def _add_row(input_dat):
        exp_id, exit_flag_id = input_dat
        sql = '''
            UPDATE `experiments`
            SET exit_flag_id={} 
            WHERE id={}'''.format(exit_flag_id, exp_id)
        cur.execute(sql)
        print('ID:{} -> {}'.format(exp_id, INDEX2NAME[exit_flag_id])) 
            
    
    print('*******', len(all_rows))
    progress_timer = TimeCounter()
    
    n_batch = mp.cpu_count()
    p = mp.Pool(n_batch)
    tot = len(all_rows)
    
    for ii in range(0, tot, n_batch):
        dat = all_rows[ii:ii + n_batch]
        
        outputs = list(map(_process_row, dat))
        
        assert len(outputs) == len(dat)
        if CHECK_FLAG:
            for x in outputs:
                _add_row(x)
                
        conn.commit()
        print('{} of {}. Total time: {}'.format(min(tot, ii + n_batch), 
                  tot, progress_timer.get_time_str()))
        
        
    
    cur.close()
    conn.close()

