# -*- coding: utf-8 -*-
"""
Created on Mon May  2 17:47:12 2016

@author: ajaver
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session, relationship
from sqlalchemy.schema import Table
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, Float, String, Sequence, ForeignKey, \
DateTime, distinct, func

from collections import Counter

from scipy.io import loadmat
import numpy as np

engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
Base = automap_base()


class SegwormFeature(Base):
    __tablename__ = 'segworm_features'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    segworm_file = Column(String(500), nullable = False) #before file_name
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    fps = Column(Float)
    total_time = Column(Float)
    n_segworm_skeletons = Column(Integer) #before n_valid_skeletons
    n_timestamps = Column(Integer)
Base.prepare(engine_v2, reflect=True)

Experiment = Base.classes.experiments;
SegwormFeature.experiment = relationship(Experiment, backref= 'segworm_features', 
                              primaryjoin="SegwormFeature.experiment_id == experiments.id")

if __name__ == '__main__':
    session_v2 = Session(engine_v2)
    if False:
        SegwormFeature.__table__.drop(engine_v2, checkfirst=True)
        SegwormFeature.__table__.create(engine_v2, checkfirst=True)
        
    segworm_feat_file = '/Users/ajaver/Documents/GitHub/Work_In_Progress/Single_Worm_Analysis/all_files/segworm_feat_files.txt'
    with open(segworm_feat_file, 'r') as fid:
        all_data = fid.read().split('\n')
    
    for ii, fullname in enumerate(all_data):
        if fullname:
            print(ii)
            segworm_dict = {}
            base_name = os.path.split(fullname)[1].replace('_features.mat', '')
            
            info = loadmat(fullname, variable_names='info', struct_as_record=False, squeeze_me=True)
            
            segworm_dict['file_name'] = fullname
            segworm_dict['fps'] = info['info'].video.resolution.fps
            segworm_dict['total_time'] = info['info'].video.length.time
            segworm_dict['n_timestamps'] = info['info'].video.length.frames
            segworm_dict['n_valid_skeletons'] = int(np.sum(info['info'].video.annotations.frames==1))
            
            expObj = session_v2.query(Experiment).filter(Experiment.base_name==base_name).one_or_none()
            if expObj is not None:
                segworm_dict['experiment_id'] = expObj.id
            
            session_v2.add(SegwormFeature(**segworm_dict))
    
    session_v2.commit()

#    engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
#    session_v2 = Session(engine_v2)
#    base_names = set(x[1] for x in data)
    
#    segInDB= session_v2.query(Experiment.base_name).\
#    filter(Experiment.base_name.in_(base_names)).all()
#    segInDB = set(x[0] for x in segInDB)
#    
#    missing_seg = base_names-segInDB
#    #%%
#    
#    engine_old = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_old')
#    session_old = Session(engine_old)
#    meta = MetaData()
#    meta.reflect(bind = engine_old, views=True)
#    locationpc_old =Table('locationpc', meta, autoload=True)
#    experiments_old = Table('experiments', meta, autoload=True)
#    
#    dd = session_old.query(experiments_old.c.wormFileName, 
#                           locationpc_old.c.computerName, locationpc_old.c.aviPath).\
#                           join(locationpc_old, locationpc_old.c.id == experiments_old.c.id).\
#                           filter(experiments_old.c.wormFileName.in_(missing_seg)).\
#                           filter(~locationpc_old.c.aviPath.ilike('%control exp%')).\
#                           all()
#    
#    DD = set((x[1].split('/')[0], os.path.split(x[2])[0]) for x in dd)
#    
#    for prefix in set(p for p,d in DD):
#        fname = prefix + '.txt'
#        if os.path.exists(fname):
#            os.remove(fname)
#    
#    for fname, d2save in DD:
#        with open(fname + '.txt', 'a') as fid:
#            fid.write(d2save + '\n')
#    
#    
#    print(Counter(list(zip(*dd))[1]))
    #%%
    #%%
#    with open('missing_basenames.txt', 'w') as fid:
#        for x in base_names-segInDB:
#            fid.write(x + '\n')