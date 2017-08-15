# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 22:01:59 2016

@author: ajaver
"""

import pymysql
import numpy as np
from collections import OrderedDict
import multiprocessing as mp

from tierpsy.helper.misc import TimeCounter

from E_get_result_summary import update_row
import sys
sys.path.append('../compare_segworm')
from read_feats import FeatsReaderComp


def _get_error(skel1, skel2):
    max_n_skel = min(skel1.shape[0], skel2.shape[0])
    delS = skel1[:max_n_skel]-skel2[:max_n_skel]
    R_error = delS[:,:,0]**2 + delS[:,:,1]**2
    skel_error = np.sqrt(np.mean(R_error, axis=1))
    
    return skel_error
    
def compare_files(skel_segworm, skeletons):
    
    skel_error = _get_error(skel_segworm, skeletons)
    switched_error = _get_error(skel_segworm, skeletons[:,::-1,:])
    
    #find nan (frames without skeletons or where the stage was moving)
    bad_errors = np.isnan(skel_error)
    if np.all(bad_errors):
        return
    
    skel_error = skel_error[~bad_errors]
    switched_error = switched_error[~bad_errors]
    
    #get percentails of error per movie
    er_05, er_50, er_95 = np.percentile(skel_error, [0.05, 0.5, 0.95])
    n_mutual_skeletons = skel_error.size
    n_switched_head_tail = np.sum(skel_error>switched_error)
    
    
    
    
    return n_mutual_skeletons, n_switched_head_tail, er_05, er_50, er_95,
    

if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', db='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    sql = '''
    SELECT e.id AS experiment_id, s.id AS segworm_info_id, 
    CONCAT(results_dir, '/', base_name, '_features.hdf5') AS tierpsy_file, segworm_file
    FROM experiments_full AS e
    JOIN segworm_info AS s ON e.id = s.experiment_id
    WHERE exit_flag = 'END'
    '''
    cur.execute(sql)
    all_rows = cur.fetchall()
    
    def _process_row(row):
        out = OrderedDict()
        out['experiment_id'] = row['experiment_id']
        out['segworm_info_id'] = row['segworm_info_id']
        
        feats_reader = FeatsReaderComp(row['tierpsy_file'], row['segworm_file'])
        try:
            skeletons, skel_segworm = feats_reader.read_skeletons()
        except:
            print('bad file :', row['tierpsy_file'], out)
            return None
        
        dd = compare_files(skel_segworm, skeletons)
        if dd is None:
            return None
        
        for k,v in zip(['n_mutual_skeletons', 'n_switched_head_tail', 'error_05th', 'error_50th', 'error_95th'], dd):
            out[k] = v
        return out
    
    
    print('*******', len(all_rows))
    progress_timer = TimeCounter()
    n_batch = mp.cpu_count()
    p = mp.Pool(n_batch)
    tot = len(all_rows)
    for ii in range(0, tot, n_batch):
        dat = all_rows[ii:ii + n_batch]
        for x in p.map(_process_row, dat):
            if x is not None:
                sql = update_row(x, table_name = 'segworm_comparisons')
                cur.execute(sql)
        conn.commit()
        print('{} of {}. Total time: {}'.format(min(tot, ii + n_batch), 
                  tot, progress_timer.get_time_str()))
    cur.close()
    conn.close()
    
    
    #%%
#    feats_reader = FeatsReaderComp(row['tierpsy_file'], row['segworm_file'])
#    skeletons, skel_segworm = feats_reader.read_skeletons()