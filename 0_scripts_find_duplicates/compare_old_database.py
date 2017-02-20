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
                                 db='single_worm_old',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    #sql_cmd = '''SELECT e.id, e.wormFileName FROM exp_annotation AS d JOIN  experiments AS e ON e.id = d.id;'''
    sql_cmd = 'SELECT * FROM experiments'
    with connection.cursor() as cursor:
        cursor.execute(sql_cmd)
        result = cursor.fetchall()
    
    db_fnames = [x['original_video'] for x in result]
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


onlyInMovies = prefix_movies-prefix_old_feats
onlyInFeats = prefix_old_feats-prefix_movies


#%%
lists_dir = '/Users/ajaver/Desktop/shafer_lab_files/'
prefix_f = 'all_files_wshafer-nas-5.txt'
f_lists = os.path.join(lists_dir, prefix_f)
with open(f_lists, 'r') as fid:
    files_lists = [x for x in fid.read().split('\n') if x.endswith('.avi') and not x.endswith('_seg.avi')]
    
    #directories that are from unclear data
    bad_parts = ['control', 'bad', 'old', 'log_file_naming_issues', 'test', 'unanalysable']
    files_lists = [x for x in files_lists if not any(bad_pre in x.lower() for bad_pre in bad_parts)]
 
    base_lists = [os.path.splitext(x.rpartition('\\')[-1])[0] for x in files_lists]
    
prefix_wshafer = set(base_lists)
print(prefix_f, len(onlyInFeats - prefix_wshafer))


prefix2copy = prefix_wshafer - prefix_movies

#%%
    
movies2copy = []
for fname in files_lists:
    bn = fname.rpartition('\\')[-1]
    for bad_e in ['.avi', '.log.csv', '.info.xml']:
        bn = bn.replace(bad_e, '')
    if bn in prefix2copy:
        movies2copy.append(fname)
            
    
    not_in_2009 = [x for x in movies2copy if not '2009' in x]



#%%
#for x in sorted(set([x.rpartition('\\')[0] for x in movies2copy])):
#    print(x)
#
#print('%%%%%%%%%%%%%%%%%%%%%%')
#for x in sorted(set([x.rpartition('\\')[-1] for x in movies2copy])):
#    print(x)



#%%
#360

from collections import Counter
import re

def print_date_counts(prefixes):
    prog = re.compile(r'20\d\d_\d\d_\d\d')
    
    all_dates = [prog.findall(x)[0] for x in prefixes]
    
    for key, val in sorted(Counter(all_dates).items()):
        print(key, '->' , val)

print_date_counts(prefix2copy)
print('%%%%%%%%%%%%%%%%%%%%%%')
print_date_counts(onlyInFeats)
print('%%%%%%%%%%%%%%%%%%%%%%')
print_date_counts(prefix_old_feats)







#%%


#
#print('In the DB but not in Local: %i' % len(notInLoc))
#print('Not DB but in Local: %i' % len(notInDB))
