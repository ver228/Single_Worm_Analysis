# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 15:52:03 2016

@author: ajaver
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
Base = automap_base()

Base.prepare(engine_v2, reflect=True)
Experiment = Base.classes.experiments;
Strain = Base.classes.strains;
SegwormFeature = Base.classes.segworm_features;
ProgressTrack = Base.classes.progress_tracks;
SegWormComparison = Base.classes.segworm_comparisons;
ProgressMask = Base.classes.progress_masks;
session_v2 = Session(engine_v2)

#%%
dd = session_v2.query(Experiment.id, Experiment.base_name, Strain.name.label('strain_name'), 
ProgressMask.mask_file, ProgressMask.total_time, ProgressMask.n_valid_frames, 
ProgressTrack.skeletons_file, ProgressTrack.features_file, ProgressTrack.n_valid_skeletons,
SegwormFeature.file_name.label('segworm_file'),
SegwormFeature.n_valid_skeletons.label('n_segworm_skeletons'),
SegWormComparison.n_mutual_skeletons
).\
join(Strain).\
join(ProgressMask).join(ProgressTrack).\
join(SegWormComparison, SegWormComparison.experiment_id == Experiment.id).\
join(SegwormFeature, SegwormFeature.experiment_id==SegWormComparison.experiment_id).\
filter(ProgressTrack.exit_flag_id == 211).\
filter(ProgressTrack.n_valid_skeletons != None).\
all()

all_data = pd.DataFrame(dd)#.fillna(0)
#%%

file_eggs = '/Users/ajaver/Documents/GitHub/Work_In_Progress/Single_Worm_Analysis/FuX/egg_list.txt'
file_noeggs = '/Users/ajaver/Documents/GitHub/Work_In_Progress/Single_Worm_Analysis/FuX/noegg_list.txt'


with open(file_eggs, 'r') as fid:
    eggs_names = [x.partition('_seg.avi')[0] for x in fid.read().split('\n') if x ]
    
with open(file_noeggs, 'r') as fid:
    noeggs_names = [x.partition('_seg.avi')[0] for x in fid.read().split('\n') if x ]
    
all_data.index  =all_data['base_name']
eggs_files = all_data.loc[eggs_names]
eggs_files = eggs_files.dropna()
noeggs_files = all_data.loc[noeggs_names]
noeggs_files = noeggs_files.dropna()
#%%
import shutil

for kk in range(50):
    save_dir = '/Volumes/UNTITLED/worm_eggs'
    for ii, row in eggs_files.sample(10).iterrows():
        print('eggs', kk, ii)
        
        mask_file = row['mask_file']
        skeletons_file = row['skeletons_file']
        
        shutil.copy(mask_file, save_dir)
        shutil.copy(skeletons_file, save_dir)

    save_dir = '/Volumes/UNTITLED/worm_noeggs'
    for ii, row in noeggs_files.sample(10).iterrows():
        print('no eggs', kk, ii)
        mask_file = row['mask_file']
        skeletons_file = row['skeletons_file']
        
        shutil.copy(mask_file, save_dir)
        shutil.copy(skeletons_file, save_dir)
