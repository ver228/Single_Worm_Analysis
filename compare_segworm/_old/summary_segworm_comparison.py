# -*- coding: utf-8 -*-
"""
Created on Thu May  5 17:17:18 2016

@author: ajaver
"""

import pandas as pd
import matplotlib.pylab as plt
import numpy as np
from functools import partial
import os 
import shutil

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
Base = automap_base()

Base.prepare(engine_v2, reflect=True)

Experiment = Base.classes.experiments;
SegwormFeature = Base.classes.segworm_features;
ExitFlag = Base.classes.exit_flags;
ProgressTrack = Base.classes.progress_tracks;
ProgressMask = Base.classes.progress_masks;
SegWormComparison = Base.classes.segworm_comparisons;

session_v2 = Session(engine_v2)

all_segworm = session_v2.query(Experiment.id, ProgressMask.mask_file,
ProgressMask.total_time, ProgressMask.n_valid_frames, 
ProgressTrack.skeletons_file, ProgressTrack.features_file,
ProgressTrack.n_valid_skeletons,
SegwormFeature.n_valid_skeletons.label('n_segworm_skeletons'),
SegwormFeature.file_name.label('segworm_file')).\
join(ProgressMask).join(ProgressTrack).\
join(SegwormFeature, SegwormFeature.experiment_id==Experiment.id).\
filter(ProgressMask.total_time >= 60).\
filter(ProgressTrack.exit_flag_id == 211).\
all()

all_segworm = pd.DataFrame(all_segworm).fillna(0)

all_segworm['skel_frac'] = all_segworm['n_valid_skeletons']/all_segworm['n_valid_frames']
all_segworm['segworm_frac'] = all_segworm['n_segworm_skeletons']/all_segworm['n_valid_frames']

#plt.figure()
#plt.plot(all_segworm['skel_frac'], all_segworm['segworm_frac'], '.')
#plt.xlabel('fraction skeletons')
#plt.ylabel('fraction skeletons (segworm)')
##%%
#all_segworm['best_n'] = (all_segworm['n_valid_skeletons']-all_segworm['n_segworm_skeletons'])/(all_segworm['n_valid_skeletons']+all_segworm['n_segworm_skeletons'])
#plt.figure()
#plt.plot(all_segworm['best_n'], '.')
#%%

if False:
    #copy sample files
    videos_15min = all_segworm[(all_segworm['total_time'] > 888) &(all_segworm['total_time'] < 910)]
    sample_videos = videos_15min.sample(25)
    save_dir = '/Users/ajaver/Desktop/Videos/single_worm/global_sample_v2/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    for ii, row in sample_videos.iterrows():
        print(ii)
        for fstr in ['mask_file', 'skeletons_file', 'features_file', 'segworm_file']:
            fname = row[fstr]
            
            shutil.copy(fname, save_dir)
            if fstr == 'skeletons_file':
                shutil.copy(fname.replace('_skeletons.', '_intensities.'), save_dir)
                shutil.copy(fname.replace('_skeletons.', '_trajectories.'), save_dir)

#%%

#dd = session_v2.query(SegWormComparison.experiment_id, \
#SegWormComparison.segworm_feature_id, SegWormComparison.n_mutual_skeletons,
#ProgressTrack.n_valid_skeletons, SegwormFeature.n_valid_skeletons).\
#join(ProgressTrack, ProgressTrack.experiment_id==SegWormComparison.experiment_id).\
#join(SegwormFeature, SegwormFeature.experiment_id==SegWormComparison.experiment_id).\
#order_by(SegWormComparison.experiment_id).all()
#
#experiment_id, segworm_feature_id, n_mutual_skeletons, \
#skel_n_valid, segworm_n_valid = map(partial(np.array, dtype=np.float), zip(*dd))

#dd = session_v2.query(ProgressMask.mask_file,
#ProgressTrack.n_valid_skeletons, SegwormFeature.n_valid_skeletons).\
#join(ProgressTrack, ProgressTrack.experiment_id==ProgressMask.experiment_id).\
#join(SegWormComparison, ProgressTrack.experiment_id==SegWormComparison.experiment_id).\
#join(SegwormFeature, SegwormFeature.experiment_id==SegWormComparison.experiment_id).\
#filter(SegwormFeature.n_valid_skeletons - ProgressTrack.n_valid_skeletons > 1000).\
#order_by(SegWormComparison.experiment_id).all()
#
#for fname, x, y in dd:
#    print(fname)
#    print(x,y)

#%%
#finished_files = session_v2.query(ProgressTrack.skeletons_file).\
#filter(ProgressTrack.exit_flag_id == 211).all()

#%%
#SegWormComparison n_mutual_skeletons
#ProgressTrack n_valid_skeletons 
#ProgressMask n_valid_frames

#dat = pd.read_hdf('comparison_errors.hdf5', 'errors', columns=['frame_number'])
#dd = dat['error'].value_counts()
#
#counts, errors = dd.values, dd.index
#
#plt.figure()
#plt.plot(errors, counts, '.')
#plt.xlim([0, 100])
##%%
#threshold_er = 60
#good_er = np.sum(counts[errors<=threshold_er])
#bad_er= np.sum(counts[errors>threshold_er])
#
#frac = good_er/(good_er + bad_er)
