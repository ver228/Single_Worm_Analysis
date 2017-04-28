#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 16:23:00 2017

@author: ajaver
"""
import pymysql
from control_experiments import movies_lists_f

def read_schafer_files():
    schafer_files_f = '/Users/ajaver/OneDrive - Imperial College London/single_worm_db/_schaffer_files/all_files_wshafer-nas-4.txt'
    with open(schafer_files_f, 'r') as fid:
        schafer_log_files = [x for x in (fid.read()).split('\n') if x]
    
    all_files = {}
    for row in schafer_log_files:
        if row.endswith('.avi') and not row.endswith('seg.avi'):
            fname = row
            bn = fname.rpartition('\\')[-1].replace('.avi', '')
        elif row.endswith('log.csv'):
            fname = row
            bn = fname.rpartition('\\')[-1].replace('.log.csv', '')
        elif row.endswith('.info.xml'):
            fname = row
            bn = fname.rpartition('\\')[-1].replace('.info.xml', '')
        else:
            continue
        
        if not bn in all_files:
            all_files[bn] = []
        
        all_files[bn].append(fname)
    return all_files

def read_local_basenames():
    #%%
    with open(movies_lists_f, 'r') as fid:
        basenames = [x.rpartition('/')[-1].replace('.avi', '') for x in fid.read().split('\n') if x]
    return basenames
    
#    conn = pymysql.connect(host='localhost', database='single_worm_db')
#    cur = conn.cursor()
#    
#    sql = '''
#    SELECT base_name
#    FROM experiments
#    '''
#    cur.execute(sql)
#    results = cur.fetchall()
#    
#    results = [x[0] for x in results]
#    
#    conn.close()
#    return results
#%%
if __name__ == '__main__':
    schaffer_files = read_schafer_files()
    local_basenames = read_local_basenames()
    
    missing_bn = set(schaffer_files.keys()) - set(local_basenames)
    files2look = {x:schaffer_files[x] for x in missing_bn}
    #%%
    files2copy = []
    missing_files= {}
    duplicated_dirs = {}
    weird_files = {}
    for bn, fullnames in files2look.items():
        dnames = {}
        fnames = []
        for fullname in fullnames:
            dd = fullname.replace('.data\\', '')
            dname, _, fname = dd.rpartition('\\')
            
            if not dname in dnames:
                dnames[dname] = []
            dnames[dname].append(fullname)
            fnames.append(fname)
        
        fnames = set(fnames)
        
        n_dir = len(dnames)
        n_files = len(fnames)
        
        
        if n_dir == 1 and n_files == 3:
            files2copy += fullnames
        elif n_files < 3:
            missing_files[bn] = fnames
        elif n_dir > 1:
            duplicated_dirs[bn] = dnames
        else:
            weird_files[bn] = fullnames
    #%% Filter duplicated files
    missplaced_f = []
    for bn, dnames in duplicated_dirs.items():
        
        
        dnames_f = [x for x in dnames.keys() if len(dnames[x]) == 3]
        if len(dnames_f) == 0:
            #flatten files
            ff = sum([dnames[x] for x in dnames], [])
            if len(ff) == 3:
                files2copy += ff
            missplaced_f += ff #let's store files that seem to be put in the wrong folder
            continue
        
        test_funcs = [
                lambda x: ("control" in x.lower() or  "old videos" in x),
                lambda x: not "unfinished" in x,
                lambda x: "finished" in x
                ]
        best_match = dnames_f
        for func in test_funcs:
            best_match = [x for x in best_match if func(x)]
            if len(best_match) == 1:
                best_match, = best_match
                break
            elif len(best_match) == 0:
                best_match = dnames_f
            
        if isinstance(best_match,list):
            #select one directory at random
            best_match = best_match[0]
        
        assert len(dnames[best_match]) == 3
    
        files2copy += dnames[best_match]
    
    
    
    #%%
    #most of the files without the three file types are log files of 
    #incomplete runs so let's filter only videos
    bn2check = []
    for bn in missing_files:
        for fname in missing_files[bn]:
            if fname.endswith('.avi') and not fname.endswith('_old.avi') and \
            not "corrupted" in fname:
                bn2check.append(bn)
    for bn in bn2check:
        lab = bn.partition('_')[-1]
        lab = '__'.join(lab.split('__')[:2])
        maybe_match = [bn for bn in files2look if lab in bn]
        maybe_files = sum([files2look[bn_m] for bn_m in maybe_match],[])
        
        ext_names = [x.rpartition('.')[-1] for x in maybe_files]
        if len(set(ext_names)) < 3:
            continue
        
        avi_files = [x for x in maybe_files if x.endswith('avi')]
        #if there is only one avi file copy all the files, otherwise select only one avi file
        if len(avi_files) == 1:
            files2copy += maybe_files
        else:
            #there is only one case where the .avi name does not match. At it is
            #because it does not have the seconds so i ignore it
            #if len(set([x.rpartition('\\')[-1] for x in avi_files])) != 1:
            #    print(set([x.rpartition('\\')[-1] for x in avi_files]))
            #    break
            
            #here I will select only the largerst name (this is a random decision)
            avi_file = max(avi_files)
            maybe_files = [x for x in maybe_files 
                           if not x.endswith('avi') or x==avi_file]
            assert any(x.endswith('avi') for x in maybe_files)
            files2copy += maybe_files
    #%%
    files2copy = sorted(files2copy)
    files2copy_v = [x for x in files2copy if x.endswith('avi')]
    
    
    with open('missing_files_schaffer_all.txt', 'w') as fid:
        fid.write('\n'.join(files2copy_v))
    
    files2copy_f = [x for x in files2copy_v if not any(d in x.lower() for d in ['bad', 'old', 'control', 'test'])]
    #
    with open('missing_files_schaffer.txt', 'w') as fid:
        fid.write('\n'.join(files2copy_f))
       
    #%%
    expected_dir = '/Volumes/behavgenom_archive$/single_worm/original_videos/single_worm_raw_bkp11'
    files2copy_s = [x.replace('\\', '/') for x in files2copy_f]
    files2copy_s = [x.replace('Y:', expected_dir) for x in files2copy_s]
    with open('new_files.txt', 'w') as fid:
        fid.write('\n'.join(files2copy_s))