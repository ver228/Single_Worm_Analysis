#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 15:49:57 2018

@author: ajaver
"""
from tierpsy.helper.params import copy_unit_conversions, read_microns_per_pixel
from tierpsy.analysis.stage_aligment.alignStageMotion import _h_add_stage_position_pix, isGoodStageAligment

import pandas as pd
import pytz
import pymysql
import os
import tables
import json
from collections import OrderedDict

experimenter_dflt = 'Celine N. Martineau, Bora Baskaner'
lab_dflt = {'name' : 'European Research Institute for the Biology of Ageing',  
            'location':'The Netherlands'}
timezone_dflt = 'Europe/Amsterdam'
media_dflt = "NGM agar low peptone"
food_dflt = "OP50"
sex_dflt = "hermaphrodite"
plate_orientation_dflt = "away"

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


def add_extra_info(base_name, results_dir, experiment_info):
    
    valid_fields = ['/mask', '/trajectories_data', '/features_timeseries']
    mask_file = os.path.join(results_dir, base_name + '.hdf5')
    skeletons_file = os.path.join(results_dir, base_name + '_skeletons.hdf5')
    features_file = os.path.join(results_dir, base_name + '_features.hdf5')
    
    def _add_exp_data(fname, experiment_info_str):
        with tables.File(fname, 'r+') as fid:
            if os.path.exists(skeletons_file) and field in fid:
                #copy data units from the skeletons file
                group_to_save = fid.get_node(field)
                copy_unit_conversions(group_to_save, skeletons_file)
            
            if '/experiment_info' in fid:
                fid.remove_node('/', 'experiment_info')
            fid.create_array('/', 'experiment_info', obj = experiment_info_str)
    
    
    experiment_info_str = bytes(json.dumps(experiment_info), 'utf-8')
    
    fnames = [mask_file, skeletons_file, features_file]
    for fname, field in zip(fnames, valid_fields):
        if os.path.exists(fname):
            _add_exp_data(fname, experiment_info_str)
    
    #finally if the stage was aligned correctly add the information into the mask file    
    if os.path.exists(mask_file) and isGoodStageAligment(skeletons_file):
        _h_add_stage_position_pix(mask_file, skeletons_file)

def db_row2dict(row):
    experiment_info = OrderedDict()
    experiment_info['base_name'] = row['base_name']
    experiment_info['who'] = experimenter_dflt
    experiment_info['lab'] = lab_dflt
    
    #add timestamp with timezone
    local = pytz.timezone(timezone_dflt) 
    
    #cast to datetime
    local_dt = local.localize(pd.to_datetime(row['timestamp']), is_dst=True)
    experiment_info['timestamp'] = local_dt.isoformat()
    
    experiment_info['arena'] = {
            "style":'petri',
            "size":35,
            "orientation":plate_orientation_dflt
            }
    
    experiment_info['media'] = media_dflt
    experiment_info['food'] = food_dflt
    
    experiment_info['strain'] = row['strain']
    experiment_info['strain_description'] = row['strain_description']
    
    
    experiment_info['sex'] = sex_dflt
    experiment_info['stage'] = row['developmental_stage']
   
    experiment_info['ventral_side'] = row['ventral_side']
    
    
    hab = "worm transferred to arena 30 minutes before recording starts."
    experiment_info['protocol'] = [
        "method in E. Yemini et al. doi:10.1038/nmeth.2560",
        hab
    ]
    
    experiment_info['days_of_adulthood'] = row['days_of_adulthood']
    experiment_info['worm_id'] = row['worm_id']
    
    return experiment_info



strains_data = [
    ('OW939', 'zgIs113[P(dat-1)::alpha-Synuclein::YFP]', 1, 1, 1),
    ('OW940', 'zgIs128[P(dat-1)::alpha-Synuclein::YFP]', 1, 1, 1),
    ('OW949', 'zgIs125[P(dat-1)::alpha-Synuclein::YFP]', 1, 1, 1),
    ('OW953', 'zgIs138[P(dat-1)::YFP]', 1, 1, 1),
    ('OW956', 'zgIs144[P(dat-1)::YFP]', 1, 1, 1)
    ]
    
if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', db='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    
    exp_file = 'ageing_celine.csv'
    experiments_df = pd.read_csv(exp_file)
    
    
    #%% delete and search for the base_name is very slow, is better to search first for what to delete (https://dba.stackexchange.com/questions/84805/delete-seems-to-hang)
    
    if False:
        print('deleting previous inserts...')
        dd = ','.join(['"{}"'.format(x) for x in experiments_df['base_name']])
        
        sql = 'select id from experiments where base_name in ({})'.format(dd)
        cur.execute(sql)
        d_id = [str(x['id']) for x in cur.fetchall()]
        if d_id:
            sql = 'delete from results_summary where experiment_id in ({})'.format(','.join(d_id))
            cur.execute(sql)
            sql = 'delete from experiments where id in ({})'.format(','.join(d_id))
            cur.execute(sql)
        
    #%%
    #remove OW945 (Celine -> "I would leave out OW945 since it contains a deletion in a coding region next to the locus of integration.")
    experiments_df = experiments_df[experiments_df['strain'] != 'OW945']
    
    #use the strain code from the CGC
    experiments_df['strain'] = experiments_df['strain'].replace({'N2' : 'AQ2947'})
    
    #rename fields to match database
    new_names = {"ventral_orientation": "ventral_side", 
                 "day":"days_of_adulthood",
                 "directory" : "results_dir"
                 }
    experiments_df = experiments_df.rename(columns=new_names)
    experiments_df['ventral_side'] = experiments_df['ventral_side'].replace({'CW':'clockwise', 'CCW':'anticlockwise'})
    
    #offset worm_id with the current number of worm_id in the database. I could read it, but I think it is better to hard code it
    worm_id_offset = 14850 #this is the number of worms currently in the database
    experiments_df['worm_id'] += worm_id_offset
    
    
    
    u_strain = experiments_df['strain'].unique()
    s_list = ','.join(['"{}"'.format(x) for x in u_strain])
    sql = 'select * from strains where name in ({});'.format(s_list)
    cur.execute(sql)
    strain_d = {x['name']:(x['id'], x['description']) for x in cur.fetchall()}
    
    
    cur.execute('select id from experimenters where name = "{}";'.format(experimenter_dflt))
    experimenter_id = cur.fetchone()['id']
    
    cur.execute('select id from arenas where name = "35mm petri dish NGM agar low peptone"')
    arena_id = cur.fetchone()['id']
    
    cur.execute('select id from habituations where name = "30m wait"')
    habituation_id = cur.fetchone()['id']
    
    
    cur.execute('select id from foods where name = "{}";'.format(food_dflt))
    food_id = cur.fetchone()['id']
    
    cur.execute('select id from sexes where name = "{}";'.format(sex_dflt))
    sex_id = cur.fetchone()['id']
    
    cur.execute('select * from developmental_stages;')
    develop_d = {x['name']:x['id'] for x in cur.fetchall()}
    
    cur.execute('select * from ventral_sides;')
    ventral_side_d = {x['name']:x['id'] for x in cur.fetchall()}
    
    #i am assuming the analysis of everything was finished
    cur.execute('select id from exit_flags where name = "END";')
    exit_flag_id = cur.fetchone()['id']
    
    bad_l = []
    for d_id, dat in experiments_df.groupby(('replicated_n', 'strain', 'w_id')):
        if dat['days_of_adulthood'].unique().size != len(dat):
            bad_l.append(dat)
    
    def _process_row(rdat):
        i_row, row = rdat
        print(i_row)
        
        row_d = row.to_dict()
        if row_d["days_of_adulthood"] == 0:
            row_d["developmental_stage"] = "L4"
        else:
            row_d["developmental_stage"] = "adult"
        
        row_d['strain_description'] = strain_d[row_d['strain']][1]
        
        del row_d['id']
        del row_d['replicated_n']
        del row_d['w_id']
        
        
        strain_id = strain_d[row_d['strain']][0]
        
        developmental_stage_id = develop_d[row_d["developmental_stage"]]
        ventral_side_id = ventral_side_d[row_d["ventral_side"]]
        
        #i probably should remove this
        original_video = os.path.join(row_d['results_dir'].replace('/results/', 'raw'), row_d['base_name'] + '.avi')
        
        dat = (row_d['base_name'], row_d['worm_id'], row_d["results_dir"],
               row_d['timestamp'], strain_id, 
        sex_id, developmental_stage_id, row_d['days_of_adulthood'], ventral_side_id,
        food_id, arena_id, habituation_id, experimenter_id, exit_flag_id, original_video)
        
        
        
        experiment_info = db_row2dict(row_d)
        add_extra_info(row_d['base_name'], row_d['results_dir'], experiment_info)
        
        
        return dat
    
    
    import multiprocessing as mp
    p = mp.Pool()
    
    all_dat = p.map(_process_row, experiments_df.iterrows())
    
    #%%
    cols = '''base_name, worm_id, results_dir, date, strain_id, sex_id, developmental_stage_id, 
    days_of_adulthood, ventral_side_id, food_id, arena_id, habituation_id, 
    experimenter_id, exit_flag_id, original_video'''
    tot = len(cols.split(','))
    
    stmt = 'INSERT INTO experiments ({}) VALUES ({})'.format(cols, ','.join(['%s']*tot))
        
    cur.executemany(stmt, all_dat)
    conn.commit()
    
    
    #%%
    
    
    #%%
    if False:
        with open('/home/ajaver@cscdom.csc.mrc.ac.uk/Github/single-worm-analysis/upload_youtube/youtube_ids.txt', 'r') as fid:
            dat = fid.read()
            
        dd = [y.split('\t') for y in [x for x in dat.split('\n') if x and '#' in x]]
        
        conn = pymysql.connect(host='localhost', db='single_worm_db')
        cur = conn.cursor()
        for bn, yid in dd:
            sql = 'UPDATE experiments SET youtube_id="{}" WHERE base_name="{}"'.format(yid, bn)
            cur.execute(sql)
        
        conn.commit()
    