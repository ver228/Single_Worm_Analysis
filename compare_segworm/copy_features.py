# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 11:00:09 2016

@author: ajaver
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

import glob
import os
import shutil

engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
Base = automap_base()

Base.prepare(engine_v2, reflect=True)
Experiment = Base.classes.experiments;

SegwormFeature = Base.classes.segworm_features;
ProgressTrack = Base.classes.progress_tracks;

main_dir = '/Users/ajaver/Desktop/Videos/single_worm/global_sample/'

files = glob.glob(os.path.join(main_dir, '*.hdf5' ))
files = [x for x in files if not x.endswith('_skeletons.hdf5') \
and not x.endswith('_features.hdf5')]

base_names = [os.path.splitext(os.path.split(x)[-1])[0] for x in files]

session_v2 = Session(engine_v2)

N = 0
for base_name in base_names:
    dd, = session_v2.query(ProgressTrack.features_file).join(Experiment).\
    filter(Experiment.base_name == base_name).one_or_none()
    
    if os.path.exists(dd):
        shutil.copy(dd, main_dir)
    else:
        print('missing: %s', dd)
        N += 1