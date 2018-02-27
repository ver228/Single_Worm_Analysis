# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 22:01:59 2016

@author: ajaver
"""

import pymysql
import numpy as np
from collections import OrderedDict
import multiprocessing as mp
import tqdm
import tables
#from tierpsy.helper.misc import TimeCounter
#from E_get_result_summary import update_row
import sys
sys.path.append('../compare_segworm')
from read_feats import FeatsReaderComp


def _get_error(skel1, skel2):
    delS = skel1 - skel2
    R_error = np.sum(delS**2, axis=2)
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
    
def _get_length(skels):
    dxy2 = np.diff(skels, axis=1)**2
    dr = np.sqrt(np.sum(dxy2, axis=2))
    ll = np.sum(dr, axis=1)
    return ll

if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', db='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    sql = '''
    SELECT e.id AS experiment_id, s.id AS segworm_info_id, 
    CONCAT(results_dir, '/', base_name, '_features.hdf5') AS tierpsy_file, segworm_file
    FROM experiments_valid AS e
    JOIN segworm_info AS s ON e.id = s.experiment_id
    WHERE exit_flag = 'END'
    '''
    cur.execute(sql)
    all_rows = cur.fetchall()
    
    def _process_row(row):
        
        #print(row['tierpsy_file'], row['segworm_file'])
        feats_reader = FeatsReaderComp(row['tierpsy_file'], row['segworm_file'])
        try:
            skeletons, skel_segworm = feats_reader.read_skeletons()
            
        except:
            print('bad file :', row['tierpsy_file'])
            return None
        
            
        max_n_skel = min(skeletons.shape[0], skel_segworm.shape[0])
        skeletons = skeletons[:max_n_skel]
        skel_segworm = skel_segworm[:max_n_skel]
        
        skel_error = _get_error(skeletons, skel_segworm)
        skel_error_switched = _get_error(skeletons[:, ::-1, :], skel_segworm)
        length_tierpsy = _get_length(skeletons)
        length_segworm = _get_length(skel_segworm)
        
        
        inds = np.ones(skel_error.size, np.int32)*row['experiment_id']
        
        rr = inds, skel_error, skel_error_switched, length_tierpsy, length_segworm
        
        #transform into a proper rec array
        return np.array(list(zip(*rr)), dtype=tab_dtypes)
    
    print('*******', len(all_rows))
    
    tab_dtypes = np.dtype([('experiment_id', np.int32),
                            ('RMSE', np.float32),
                             ('RMSE_switched', np.float32),
                             ('length_tierpsy', np.float32),
                             ('length_segworm', np.float32)
                             ])
    
    TABLE_FILTERS = tables.Filters(
    complevel=5,
    complib='zlib',
    shuffle=True,
    fletcher32=True)
    
    with tables.File('all_skeletons_comparisons.hdf5', 'w') as fid:
        tab = fid.create_table('/',
                            "data",
                            tab_dtypes,
                            expectedrows = 253994000,
                            filters = TABLE_FILTERS)
        #n_batch = mp.cpu_count()
        n_batch = 15
        #p = mp.Pool(n_batch)
        tot = len(all_rows)
        for ii in tqdm.tqdm(range(0, tot, n_batch)):
            
            dat = all_rows[ii:ii + n_batch]
            #res = [x for x in p.map(_process_row, dat) if x is not None]
            res = [x for x in map(_process_row, dat) if x is not None]
            
            tab.append(np.concatenate(res))
            
            fid.flush()
            