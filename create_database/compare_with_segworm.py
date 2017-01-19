# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 22:01:59 2016

@author: ajaver
"""

import tables
import os
import numpy as np
from scipy.io import loadmat

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, relationship

from sqlalchemy import Column, Integer, Float, ForeignKey

engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
Base = automap_base()

class SegWormComparison(Base):
    __tablename__ = 'segworm_comparisons'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    segworm_feature_id = Column(Integer, ForeignKey('segworm_features.id'))
    n_mutual_skeletons = Column(Integer)
    error_05th = Column(Float)
    error_50th = Column(Float)
    error_95th = Column(Float)

Base.prepare(engine_v2, reflect=True)
Experiment = Base.classes.experiments;
SegwormFeature = Base.classes.segworm_features;
ExitFlag = Base.classes.exit_flags;
ProgressTrack = Base.classes.progress_tracks;

class AllErrors(tables.IsDescription):
    experiment_id = tables.Int32Col(pos=0)
    frame_number = tables.Int32Col(pos=1)
    error = tables.Int32Col(pos=2)
    error_switched = tables.Int32Col(pos=3)

if __name__ == '__main__':
    session_v2 = Session(engine_v2)
    
    errors_file = 'comparison_errors.hdf5'
    if False:
        SegWormComparison.__table__.drop(engine_v2, checkfirst=True)
        SegWormComparison.__table__.create(engine_v2, checkfirst=True)
        
        table_filters = tables.Filters(complevel=5, complib='zlib', shuffle=True, fletcher32=True)
        with tables.File(errors_file, 'w') as fid:
            fid.create_table('/', 'errors', AllErrors, filters=table_filters)
    
    calculated_ids = session_v2.query(SegWormComparison.segworm_feature_id).all()
    if calculated_ids:
        calculated_ids = list(zip(*calculated_ids))[0]
    
    finished_id = session_v2.query(ExitFlag.id).filter(ExitFlag.name == 'Finished').one()[0]

    all_segworm = session_v2.query(SegwormFeature, Experiment, ProgressTrack).\
    join(Experiment).join(ProgressTrack).\
    filter(ProgressTrack.exit_flag_id == finished_id).\
    filter(~SegwormFeature.id.in_(calculated_ids)).\
    order_by(SegwormFeature.id).all()
    
    for segwormObj, expObj, proTrackObj in all_segworm:
        
        base_name = expObj.base_name
        segworm_feat_file = segwormObj.file_name
        feat_file = proTrackObj.features_file
        skel_file = proTrackObj.skeletons_file
        
        with tables.File(feat_file, 'r') as fid:
            if '/features_means' in fid and \
            fid.get_node('/features_means').attrs['has_finished'] and \
            fid.get_node('/features_timeseries').shape[0]>0:
                skeletons = fid.get_node('/skeletons')[:]
                frame_range = fid.get_node('/features_events/worm_1')._v_attrs['frame_range']
        
            #length_avg = np.nanmean(fid.get_node('/features_timeseries').col("length"))
        
        #load rotation matrix to compare with the segworm
        with tables.File(skel_file, 'r') as fid:
            rotation_matrix = fid.get_node('/stage_movement')._v_attrs['rotation_matrix']
        
        #pad the beginign with np.nan to have the same reference as segworm (frame 0)
        skeletons = np.pad(skeletons, [(frame_range[0],0), (0,0), (0,0)], 
                       'constant', constant_values = np.nan)
        
        #load segworm data
        fvars = loadmat(segworm_feat_file, struct_as_record=False, squeeze_me=True)
        segworm_x = -fvars['worm'].posture.skeleton.x.T
        segworm_y = -fvars['worm'].posture.skeleton.y.T
        segworm = np.stack((segworm_x,segworm_y), axis=2)
        
        #correct in case the data has different size shape
        max_n_skel = min(segworm.shape[0], skeletons.shape[0])
        skeletons = skeletons[:max_n_skel]
        segworm = segworm[:max_n_skel]
        
        #shift the skeletons coordinate system to one that diminushes the errors the most.
        seg_shift = np.nanmedian(skeletons-segworm, axis = (0,1))
        segworm += seg_shift
        
        #calculate the square root of the mean squared error
        R_error = np.sum((skeletons-segworm)**2, axis=2)
        skel_error = np.sqrt(np.mean(R_error, axis=1))
        
        #find nan (frames without skeletons or where the stage was moving)
        bad_errors = np.isnan(skel_error)
        if np.all(bad_errors):
            continue
        frame_numbers = np.where(~bad_errors)[0];
        skel_error = skel_error[frame_numbers]
        
        #calculate the square root of the mean squared error of the inverted skeletons.
        #the switched srme should be less than the original if old and new data disagree
        R_error_switched = np.sum((skeletons[:,::-1,:]-segworm)**2, axis=2)
        switched_error = np.sqrt(np.mean(R_error_switched, axis=1))
        switched_error = switched_error[frame_numbers]
        
        #get percentails of error per movie
        er_05, er_50, er_95= np.percentile(skel_error, [0.05, 0.5, 0.95])
        n_mutual_skeletons = skel_error.size
        
        #save data in the database and hdf5 file
        segworm_comparision_dict = {'experiment_id':expObj.id, \
        'segworm_feature_id':segwormObj.id, 'n_mutual_skeletons':n_mutual_skeletons,
        'error_05th':float(er_05), 'error_50th':float(er_50), 'error_95th':float(er_95)}
        session_v2.add(SegWormComparison(**segworm_comparision_dict))
        
        dat2add = [(expObj.id, tt, er, er_s) for tt, er, er_s in 
        zip(frame_numbers, np.round(skel_error).astype(np.int), 
            np.round(switched_error).astype(np.int))]
        
        with tables.File(errors_file, 'r+') as fid:
            errors_table = fid.get_node('/', 'errors')
            errors_table.append(dat2add)
        
        print(segwormObj.id)
        session_v2.commit()
        