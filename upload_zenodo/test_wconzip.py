#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 15:01:31 2017

@author: ajaver
"""
import os
import pymysql
import zipfile
import multiprocessing as mp


def _process_row(row):
    experiment_id = row['experiment_id']
    fname = os.path.join(row['results_dir'], row['filename'])
    
    try:
        with zipfile.ZipFile(fname) as zf:
            ret = zf.testzip()
    except:
        print("error: ", experiment_id)
        ret = -3
        
    return experiment_id, ret

conn = pymysql.connect(host='localhost', database='single_worm_db')
cur = conn.cursor(pymysql.cursors.DictCursor)

sql = '''
SELECT Z.experiment_id, results_dir, filename
FROM experiments AS e
JOIN 
(SELECT experiment_id, filename
FROM zenodo_files 
JOIN file_types AS f ON f.id = file_type_id
WHERE f.name = 'wcon') AS Z
ON e.id = experiment_id
ORDER BY experiment_id
'''

cur.execute(sql)
data = cur.fetchall()


n_batch = 40

p = mp.Pool(n_batch)

results_d = []
for ii in range(0, len(data), n_batch):
    chunk = data[ii:ii + n_batch]
    
    dd = p.map(_process_row, chunk)
    results_d.append(dd)
    
    print(ii + n_batch, len(data))

(1300, 1751, 1759, 2097, 2120, 11987, 11995, 12041, 12626, 12814, 12985, 13201, 13812, 14040, 14289)