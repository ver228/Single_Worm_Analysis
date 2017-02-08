# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 17:03:51 2016

@author: ajaver
"""
import pandas as pd

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
dd = session_v2.query(Experiment.id, Strain.name.label('strain_name'), 
ProgressMask.mask_file, ProgressMask.total_time, ProgressMask.n_valid_frames, 
ProgressTrack.skeletons_file, ProgressTrack.features_file, ProgressTrack.n_valid_skeletons,
SegwormFeature.segworm_file,
SegwormFeature.n_segworm_skeletons,
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
import shutil

save_dir = '/Users/ajaver/Desktop/Videos/individual_feat_files'
top_strains = all_data['strain_name'].value_counts()

top10_strains = top_strains.index[:3]

for strain in top10_strains:
    feat_files = all_data.loc[all_data['strain_name'] == strain, 'features_file']
    
    for feat_file in feat_files.sample(10):
        shutil.copy(feat_file, save_dir)
        




