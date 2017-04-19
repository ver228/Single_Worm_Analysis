# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 12:09:16 2016

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

dd = session_v2.query(Experiment.id, Experiment.base_name,
ProgressTrack.skeletons_file, ProgressTrack.n_valid_skeletons, 
ProgressTrack.first_frame, ProgressTrack.last_frame,
ProgressMask.n_valid_frames, ProgressTrack.n_valid_skeletons).\
join(ProgressMask, ProgressMask.experiment_id == Experiment.id).\
join(ProgressTrack, ProgressTrack.experiment_id==Experiment.id).\
all()

errors_df = pd.DataFrame(dd)#.fillna(0)
#%%
errors_df['frac_track'] = (errors_df['last_frame'] - 
errors_df['first_frame'] + 1)/errors_df['n_valid_frames']
errors_df = errors_df.dropna()