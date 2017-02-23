#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 14:26:30 2017

@author: ajaver
"""
import os
ff = '/Users/ajaver/Documents/GitHub/single-worm-analysis/files_lists/single_worm.txt'
with open(ff, 'r') as fid:
    flist = fid.read()
    flist = [x.replace('//', '/') for x in flist.split('\n') if x]



new_flist = []
bad_flist = []  

def _get_existing(fname):
    old_dir_p = '/Volumes/behavgenom_archive$/single_worm/'
    new_dir_p = '/Volumes/behavgenom_archive$/single_worm/orignal_videos/single_worm_raw_bkp{}/'
    for idir in range(1, 12):
        new_fname = fname.replace(old_dir_p, new_dir_p.format(idir))
        if os.path.exists(new_fname):
            return new_fname
    return ''

for ii, fname in enumerate(flist):
    print(ii+1, len(flist))
    new_fname = _get_existing(fname)
    
    if new_fname:
        new_flist.append(new_fname)
    else:
        bad_flist.append(fname)
        break
    
 
assert len(new_flist) == len(flist)
#%%
with open('single_worm.txt', 'w') as fid:
    fid.write('\n'.join(new_flist))