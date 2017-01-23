#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 16:23:00 2017

@author: ajaver
"""

import os
from MWTracker.analysis.compress_add_data.getAdditionalData import getAdditionalFiles

from control_experiments import F_LISTS_DIR, movies_lists_f

unassinged_addfiles_lists_f = os.path.join(F_LISTS_DIR, 'all_log_files.txt')#'unassinged_addfiles.txt')
missing_addfiles_lists_f = os.path.join(F_LISTS_DIR, 'missing_addfiles.txt')

def save_miss_add_files():
    with open(movies_lists_f, 'r') as fid:
        full_movie_files = fid.read().split('\n')
        full_movie_files = [fname for fname in full_movie_files if fname.endswith('.avi')]
    
    missing_additional_files = []
    
    for ii, fname in enumerate(full_movie_files): 
        print(ii, len(full_movie_files))
        if not os.path.exists(fname):
            continue
        try:
            info_file, stage_file = getAdditionalFiles(fname)
        except (FileNotFoundError, IOError):
            missing_additional_files.append(fname)
        
    with open(missing_addfiles_lists_f, 'w') as fid:
        fid.write('\n'.join(missing_additional_files))

        #%%
if __name__ == '__main__':
    with open(missing_addfiles_lists_f, 'r') as fid:
        missing_additional_files = [os.path.realpath(x) for x in (fid.read()).split('\n') if x]
    
    #find /Volumes/SAMSUNG/ -name '*.log.csv' -or -name '*.info.xml' > unassinged_addfiles.txt
    with open(unassinged_addfiles_lists_f, 'r') as fid:
        unassinged_addfiles = [os.path.realpath(x) for x in (fid.read()).split('\n') if x]
    
    #%%
    
    
    v_dict = {}
    for v_file in missing_additional_files:
        dname, basename = os.path.split(v_file)
        prefix = os.path.splitext(basename)[0]
        v_dict[prefix] = dname
    #%%
    files2move = []
    foundfiles = []
    for fname in unassinged_addfiles:
        dname, basename = os.path.split(fname)
        prefix = basename.replace('.log.csv', '').replace('.info.xml', '')
        
        if prefix in v_dict:
            files2move.append((v_dict[prefix], fname))
            foundfiles.append(os.path.join(v_dict[prefix], prefix + '.avi'))
    
    notfoundfiles = set(missing_additional_files) - set(foundfiles)
    
    #%%
    import shutil
    for dstdir, src in files2move:
        shutil.copy(src, dstdir)


