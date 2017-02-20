#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 13:48:10 2017

@author: ajaver
"""


if __name__ == '__main__':
    #assuming a previous split where the files are ordered by file size
    ff = ['/Users/ajaver/Documents/GitHub/single-worm-analysis/all_agar_1.txt',
    '/Users/ajaver/Documents/GitHub/single-worm-analysis/all_agar_2.txt']
    
    
    fid = [open(x, 'r') for x in ff]
    flist = [x.read().split('\n') for x in fid]
    [x.close() for x in fid]
    
    max_f = max(len(x) for x in flist)
    #flist = [x if len(x) == max_f else x.append('') for x in flist]
     
    flist = [x if len(x) == max_f else x + [''] for x in flist]
    assert all(len(x) == max_f for x in flist)
    
    file_list = [x for x in sum(map(list, zip(*flist)), []) if x]
    
    
    n_files = 3
    divided_files = [[] for i in range(n_files)]
                
    
    for ii, fname in enumerate(file_list):
        ind = ii % n_files
        divided_files[ind].append(fname)
    
    for ii, f_list in enumerate(divided_files):
        with open('missing_{}.txt'.format(ii+1), 'w') as fid:
            fid.write('\n'.join(f_list))