# -*- coding: utf-8 -*-
"""
Created on Wed May 18 12:07:42 2016

@author: ajaver
"""
from sqlalchemy import create_engine, MetaData, UniqueConstraint
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, DateTime, distinct, func
from sqlalchemy.schema import Table
from sqlalchemy.ext.automap import automap_base

import json
import os
import tables
import stat
import shutil

from MWTracker.featuresAnalysis.obtainFeaturesHelper import switchCntSingleWorm, isBadVentralOrient

if __name__ == '__main__':
    engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
    Base = automap_base()
    Base.prepare(engine_v2, reflect=True)
    Experiment = Base.classes.experiments
    Strain = Base.classes.strains
    Gene = Base.classes.genes
    ProgressMask = Base.classes.progress_masks
    session_v2 = Session(engine_v2)
    
    #all_data = session_v2.query(ProgressMask.mask_file).\
    #join(Experiment, Experiment.id == ProgressMask.experiment_id).\
    #join(Strain).join(Gene).filter(Gene.name=='goa-1').all()
    
    
#    dst_dir = '/Users/ajaver/Desktop/Videos/single_worm/goa-1/'
#    if not os.path.exists(dst_dir):
#        os.makedirs(dst_dir)
#    
#    for ii, dat in enumerate(all_data):
#        print(ii)
#        shutil.copy(dat[0], dst_dir)
    #%%
    SegwormFeatures = Base.classes.segworm_features
    ProgressTracks = Base.classes.progress_tracks
    
    goa_feats = session_v2.query(SegwormFeatures.file_name, ProgressTracks.exit_flag_id).\
    filter(SegwormFeatures.file_name.ilike('%goa-1%')).\
    filter(~SegwormFeatures.file_name.ilike('%egl-30;goa-1%')).\
    join(Experiment, Experiment.id == SegwormFeatures.experiment_id).\
    join(ProgressTracks, Experiment.id == ProgressTracks.experiment_id).\
    all()
    #%%
    for file_name, exit_flag_id in goa_feats:
        print(os.path.split(file_name)[1], exit_flag_id)
    #%%
    import tables, glob, os
    main_dir = '/Users/ajaver/Desktop/Videos/single_worm/goa-1/Results/'
    files = glob.glob(os.path.join(main_dir, '*_skeletons.hdf5'))
    for skel_file in files:
        with tables.File(skel_file, 'r+') as fid:
            if fid.get_node('/stage_movement')._v_attrs['has_finished'][0] == 1:
                print(os.path.split(skel_file)[1])