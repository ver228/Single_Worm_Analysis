# -*- coding: utf-8 -*-
"""
Created on Tue May 10 13:50:38 2016

@author: ajaver
"""
import pandas as pd
import matplotlib.pylab as plt
import numpy as np
import seaborn as sns
import shutil
import os

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
dd = session_v2.query(Experiment.id, Strain.name.label('strain_name'), Strain.genotype, ProgressMask.mask_file, \
SegWormComparison.error_05th, SegWormComparison.error_50th, SegWormComparison.error_95th,
SegWormComparison.n_mutual_skeletons, ProgressTrack.n_valid_skeletons, 
SegwormFeature.n_valid_skeletons.label('n_segworm_skeletons')).\
join(Strain).\
join(ProgressMask, ProgressMask.experiment_id == Experiment.id).\
join(SegWormComparison, SegWormComparison.experiment_id == Experiment.id).\
join(ProgressTrack, ProgressTrack.experiment_id==SegWormComparison.experiment_id).\
join(SegwormFeature, SegwormFeature.experiment_id==SegWormComparison.experiment_id).\
order_by(SegWormComparison.error_50th).\
filter(ProgressTrack.n_valid_skeletons != None).\
all()

errors_df = pd.DataFrame(dd)#.fillna(0)
#%%
errors_df['segworm_frac'] = errors_df['n_valid_skeletons']/(errors_df['n_valid_skeletons']+errors_df['n_segworm_skeletons'])

##%%
#with sns.plotting_context(font_scale=0.5):
#    for err_str in ['error_50th']:#["error_05th", "error_50th", "error_95th"]:
#        plt.figure()
#        g = sns.boxplot(x="strain_name", y=err_str, data=errors_df);
#        locs, labels = plt.xticks()
#        g.set_xticklabels(labels, rotation=90, fontsize='x-small')
#%%
#SegWormComparison n_mutual_skeletons
#ProgressTrack n_valid_skeletons 
#ProgressMask n_valid_frames


dat = pd.read_hdf('../build_database/comparison_errors.hdf5', 'errors', columns=['frame_number'])
#%%

plt.figure()
dd = dat['error'].value_counts()
counts, errors = dd.values, dd.index
plt.plot(errors, counts, '.')

dd = dat[['error', 'error_switched']].min(axis=1).value_counts()
counts_switched, errors_switched = dd.values, dd.index

plt.figure()
plt.plot(errors_switched, counts_switched, '.')
plt.xlim([0, 1000])
#%%
plt.figure()
plt.plot(errors, counts, '.')
plt.plot(errors_switched, counts_switched, '.')
plt.ylim([0, np.max(counts[40:])])
plt.xlim([0, 1000])

#%%
#0.031447410369150837

dat['bad_headtail'] = dat['error']>dat['error_switched']

dat_gexp = dat.groupby('experiment_id')
switch_frac = dat_gexp.agg({'bad_headtail':np.mean})

print('frac switched {}'.format(dat['bad_headtail'].mean()))
#%%
dd = session_v2.query(Experiment.id, Strain.name.label('strain_name'), 
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

all_data.index = all_data['id']
all_data['switch_frac'] = switch_frac.loc[all_data.index]

conflict_HT = all_data[(all_data['switch_frac']>0.25) & (all_data['total_time'] > 888) &(all_data['total_time'] < 910)]
#%%
#large errors
if False:
    save_dir = '/Users/ajaver/Desktop/Videos/single_worm/large_errors/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    bad_ids = np.unique(dat.loc[dat['error']>1000, 'experiment_id'])
    for bad_id in bad_ids:
        row = all_data.loc[bad_id]
        for fstr in ['mask_file', 'skeletons_file', 'features_file', 'segworm_file']:
            fname = row[fstr]
            shutil.copy(fname, save_dir)


#%%
if False:
    #copy sample files
    sample_videos = conflict_HT.sample(25)
    save_dir = '/Users/ajaver/Desktop/Videos/single_worm/switched_sample/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    for ii, row in sample_videos.iterrows():
        print(ii)
        for fstr in ['mask_file', 'skeletons_file', 'features_file', 'segworm_file']:
            fname = row[fstr]
            shutil.copy(fname, save_dir)
#%%

#np.random.choice(conflict_HT.index, 50)



#%%
