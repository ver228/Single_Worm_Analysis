# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 14:45:16 2016

@author: ajaver
"""
import pymysql.cursors

import os
from control_experiments import F_LISTS_DIR, movies_lists_f
from search_missing_addfiles import missing_addfiles_lists_f

feats_lists_f = os.path.join(F_LISTS_DIR, 'segworm_feat_files.txt')


def names_old_db():

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='ajaver',
                                 db='worm_db',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    #sql_cmd = '''SELECT e.id, e.wormFileName FROM exp_annotation AS d JOIN  experiments AS e ON e.id = d.id;'''
    sql_cmd = 'SELECT * FROM experiments'
    with connection.cursor() as cursor:
        cursor.execute(sql_cmd)
        result = cursor.fetchall()
    
    db_fnames = [x['wormFileName'] for x in result]
    db_fnames = set(db_fnames)
    return db_fnames

#%%
def get_prefix_list(fname, fext):
    with open(fname, 'r') as fid:
        files_list = fid.read().split('\n')
    files_list = [x for x in files_list if not '_seg.avi' in x and x]
    directories, basenames = zip(*map(os.path.split, files_list))
    prefix_list = set([x.replace(fext, '') for x in basenames])
    return prefix_list



prefix_movies = get_prefix_list(movies_lists_f, '.avi')
prefix_old_feats = get_prefix_list(feats_lists_f, '_features.mat')
prefix_missing = get_prefix_list(missing_addfiles_lists_f, '.avi')


notInMovies = prefix_movies-prefix_old_feats
notInFeats = prefix_old_feats-prefix_movies


#%%


#%%


#
#print('In the DB but not in Local: %i' % len(notInLoc))
#print('Not DB but in Local: %i' % len(notInDB))
