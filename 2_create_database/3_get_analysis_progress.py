# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:17:35 2016

@author: ajaver
"""

import os
import pymysql.cursors
from tierpsy.processing.AnalysisPoints import AnalysisPoints
from tierpsy.analysis.stage_aligment.alignStageMotion import isGoodStageAligment
from tierpsy.analysis.contour_orient.correctVentralDorsal import isBadVentralOrient
from tierpsy.analysis.compress.processVideo import isGoodVideo
from tierpsy.analysis.compress_add_data.getAdditionalData import hasAdditionalFiles
import tierpsy
params_dir = os.path.join(os.path.dirname(tierpsy.__file__), 'misc', 'param_files')
ON_FOOD_JSON = os.path.join(params_dir, 'single_worm_on_food.json')



from helper.db_info import add_exp_info

def get_points2check():
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor()
    cur.execute('USE `single_worm_db`;')
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
POINTS2CHECK_M =  [x for x in POINTS2CHECK if x not in ['COMPRESS', 'COMPRESS_ADD_DATA']]
    
#%%
def get_last_finished(ap_obj, cur, points2check):
    def _get_flag_name(_ap_obj):
        unfinished = _ap_obj.getUnfinishedPoints(points2check)
        if not unfinished:
            return 'END'
        else:
            if not 'STAGE_ALIGMENT' in unfinished:
                if not isGoodStageAligment(_ap_obj.file_names['skeletons']):
                    return 'FAIL_STAGE_ALIGMENT'
            
            if not 'CONTOUR_ORIENT' in unfinished:
                if isBadVentralOrient(_ap_obj.file_names['skeletons']):
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


def get_rows(last_valid=''):
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    cur.execute('USE `single_worm_db`;')
    
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
    UPDATE_INFO = False
    NO_CHECK = False
    last_valid = 'WCON_EXPORT'#''# #'FEAT_CREATE' 
    
    conn, all_rows = get_rows(last_valid)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    print('*******', len(all_rows))
    for irow, row in enumerate(all_rows):
        print('{} of {}'.format(irow+1, len(all_rows)))
        main_file, masks_dir, results_dir, points2check = get_results_files(row)
        if not NO_CHECK:
            ap_obj = AnalysisPoints(main_file, masks_dir, results_dir, ON_FOOD_JSON)
            exit_flag_id, last_point = get_last_finished(ap_obj, cur, points2check)
            
            sql = '''
            UPDATE `experiments`
            SET exit_flag_id={} 
            WHERE id={}'''.format(exit_flag_id, row['id'])
            cur.execute(sql)
            conn.commit()
        
            print('ID:{} -> {}'.format(row['id'], last_point))
        
        
        if UPDATE_INFO:
            
            add_exp_info(cur, row['base_name'], masks_dir, results_dir)

        
    cur.close()
    conn.close()
    
    
    
            

#    

