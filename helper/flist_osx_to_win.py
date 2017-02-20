# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 14:22:08 2017

@author: worm_rig
"""

fname = r'C:\Users\wormrig\Documents\GitHub\Single_Worm_Analysis\files_lists\vid_on_food_2.txt'



old_root = '/Volumes/behavgenom_archive$/single_worm/thecus//'
new_root = r'Y:\single_worm\thecus'
with open(fname, 'r') as fid:
    files = fid.read()
    files = [x.replace(old_root, new_root) for x in files.split('\n') if x]
    files = [x.replace('/', '\\') for x in files]
    

new_fname = fname.replace('.txt', '_win.txt')
with open(new_fname, 'w') as fid:
    fid.write('\n'.join(files))
    