# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:17:35 2016

@author: ajaver
"""

from sqlalchemy import create_engine, MetaData, UniqueConstraint
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, Float, String, Sequence, ForeignKey, \
DateTime, distinct, func
from sqlalchemy.schema import Table

import json
import os
import tables
import numpy as np
import pandas as pd

from MWTracker.batchProcessing.trackSingleWorker import getStartingPoint, checkpoint_label, \
isBadStageAligment, hasExpCntInfo, constructNames

from MWTracker.batchProcessing.compressMultipleFilesHelper import isBadMask
from MWTracker.compressVideos.getAdditionalData import getAdditionalFiles
from MWTracker.featuresAnalysis.obtainFeatures import getFPS

dict_mask_flags = {'Missed auxiliary files':101, 'Incomplete mask file':102, 'Finished mask file':103}

dict_track_flags = {
'TRAJ_CREATE':(201, 'Create trajectories'), 
'TRAJ_JOIN':(202, 'Join trajectories'), 'SKE_CREATE':(203, 'Create skeletons'), 
'SKE_ORIENT':(204, 'Orient skeletons movement'), 'SKE_FILT':(205, 'Filter skeletons'),
'STAGE_ALIGMENT':(206,'Strage aligment'), 
'INT_PROFILE':(207, 'Intensity profile'), 'INT_SKE_ORIENT':(208, 'Orient skeletons intensity'), 
'CONTOUR_ORIENT':(209, 'Orient ventral side'),
'FEAT_CREATE':(210, 'Obtain features'), 'END':(211, 'Finished'), 
}

engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
Base = automap_base()


class ExitFlag(Base):
    __tablename__ = 'exit_flags'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    track_checkpoint = Column(String(20))
    
class ProgressMask(Base):
    __tablename__ = 'progress_masks'
    __table_args__ = {'extend_existing': True}
    experiment_id = Column(Integer, ForeignKey('experiments.id'), primary_key=True)
    exit_flag_id = Column(Integer, ForeignKey('exit_flags.id'))
    mask_file = Column(String(500))
    n_valid_frames = Column(Integer)
    n_missing_frames = Column(Integer)
    fps = Column(Float)
    total_time = Column(Float)
    exit_flag = relationship(ExitFlag, primaryjoin="ProgressMask.exit_flag_id == ExitFlag.id")
    
class ProgressTrack(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'progress_tracks'
    experiment_id = Column(Integer, ForeignKey('experiments.id'), primary_key=True)
    exit_flag_id = Column(Integer, ForeignKey('exit_flags.id'))
    skeletons_file = Column(String(500))
    features_file = Column(String(500))
    n_segmented_skeletons = Column(Integer)
    n_filtered_skeletons = Column(Integer)
    n_valid_skeletons = Column(Integer)
    n_timestamps = Column(Integer)
    first_frame = Column(Integer)
    last_frame = Column(Integer)
    
    exit_flag = relationship(ExitFlag, primaryjoin="ProgressTrack.exit_flag_id == ExitFlag.id")

Base.prepare(engine_v2, reflect=True)
Experiment = Base.classes.experiments
OriginalVideo = Base.classes.original_videos

all_tables = [ExitFlag, ProgressMask, ProgressTrack]
if __name__ == '__main__':
    
    session_v2 = Session(engine_v2)
    
    if False:
        #create the tables from scratch
        for new_table in all_tables[::-1]:
            new_table.__table__.drop(engine_v2, checkfirst=True)
        
        for new_table in all_tables:
            new_table.__table__.create(engine_v2, checkfirst=True)
        
        for name in dict_mask_flags:
            session_v2.add(ExitFlag(id=dict_mask_flags[name], name = name))
        
        for track_checkpoint in dict_track_flags:
            flag_id, name = dict_track_flags[track_checkpoint]
            session_v2.add(ExitFlag(id=flag_id, name = name, track_checkpoint=track_checkpoint))
        
        session_v2.commit()
    
    calculated_ids = session_v2.query(ProgressMask.experiment_id).all()
    if len(calculated_ids)>0:
        calculated_ids = list(zip(*calculated_ids))[0]
    
    if False:
        #Recalculate videos that were not finished (END)
        not_finished = session_v2.query(ProgressTrack.experiment_id).\
        filter(ProgressTrack.exit_flag_id != dict_track_flags['END'][0]).all()
        if len(not_finished) > 0:
            not_finished = set(list(zip(*not_finished))[0])
            calculated_ids = set(calculated_ids) - not_finished
    
    all_data = session_v2.query(OriginalVideo, Experiment).join(Experiment).\
    filter(~Experiment.id.in_(calculated_ids)).all()
    
    for n_row, (vid_obj, exp_obj) in enumerate(all_data):
        video_file = os.path.join(vid_obj.directory, vid_obj.name)
        
        mask_dir = vid_obj.directory.replace('/thecus/','/MaskedVideos/')
        masked_image_file = os.path.join(mask_dir, exp_obj.base_name + '.hdf5')
        results_dir = vid_obj.directory.replace('/thecus/','/Results/')
        
        progress_mask = {'experiment_id':exp_obj.id}
        try:
            #this function will throw and error if the .info.xml or .log.csv are not found
            info_file, stage_file = getAdditionalFiles(video_file)
            if not os.path.exists(masked_image_file):
                raise FileNotFoundError
            
            progress_mask['mask_file'] = masked_image_file
            if isBadMask(masked_image_file):
                progress_mask['exit_flag_id'] = dict_mask_flags['Incomplete mask file']
            else:
                with tables.File(masked_image_file, 'r') as fid:
                    progress_mask['n_valid_frames'] = int(fid.get_node('/mask').shape[0])
                    
                fps, _ = getFPS(masked_image_file, None)
                if not fps is None:
                    with tables.File(masked_image_file, 'r') as fid:
                        timestamp_time = fid.get_node('/timestamp/time')[:]
                        timestamp_ind = fid.get_node('/timestamp/raw')[:]
                        #sometimes only the last frame is nan
                        timestamp_ind = timestamp_ind[~np.isnan(timestamp_time)]
                        timestamp_time = timestamp_time[~np.isnan(timestamp_time)]
                        assert timestamp_ind.size == timestamp_time.size
                        
                        progress_mask['n_missing_frames'] = int(timestamp_ind[-1] - progress_mask['n_valid_frames'] + 1)
                        progress_mask['total_time'] = float(timestamp_time[-1])
                        progress_mask['fps'] = float(fps)
                
                progress_mask['exit_flag_id'] = dict_mask_flags['Finished mask file']
        except (IOError, FileNotFoundError):
            progress_mask['exit_flag_id'] = dict_mask_flags['Missed auxiliary files']
        
        session_v2.merge(ProgressMask(**progress_mask))

        if progress_mask['exit_flag_id'] == dict_mask_flags['Finished mask file']:
            base_name, trajectories_file, skeletons_file, features_file, \
            feat_manual_file, intensities_file = constructNames(masked_image_file, results_dir)
            
            checkpoint_ind = getStartingPoint(masked_image_file, results_dir)
            current_point = checkpoint_label[checkpoint_ind]
            if current_point == 'INT_PROFILE' and isBadStageAligment(skeletons_file):
                current_point = 'STAGE_ALIGMENT'
            if current_point == 'FEAT_CREATE' and hasExpCntInfo(skeletons_file):
                current_point = 'CONTOUR_ORIENT'
            
            track_progress_flag, _ = dict_track_flags[current_point]
            
            progress_track = {'experiment_id':exp_obj.id, 'exit_flag_id' : track_progress_flag}
            if track_progress_flag > dict_track_flags['SKE_CREATE'][0]:
                progress_track['skeletons_file'] = skeletons_file
                
                with pd.HDFStore(skeletons_file, 'r') as fid:
                    trajectories_data = fid['/trajectories_data']
                    if len(trajectories_data) > 0:
                        progress_track['n_segmented_skeletons'] = int(trajectories_data['has_skeleton'].sum())
                        progress_track['n_filtered_skeletons'] = int(trajectories_data['is_good_skel'].sum())
                        progress_track['first_frame'] = int(trajectories_data['frame_number'].min())
                        progress_track['last_frame'] = int(trajectories_data['frame_number'].max())
            
            if track_progress_flag > dict_track_flags['FEAT_CREATE'][0]:
                progress_track['features_file'] = features_file
                with tables.File(features_file, 'r') as fid:
                    skel = fid.get_node('/skeletons')[:,0,0] #use it as a proxy of valid skeletons
                    if skel.size > 0:
                        
                        progress_track['n_valid_skeletons'] = int(np.sum(~np.isnan(skel)))
                        progress_track['n_timestamps'] = len(skel)
                    else:
                        progress_track['n_valid_skeletons'] = 0
                        progress_track['n_timestamps'] = 0
                
            session_v2.merge(ProgressTrack(**progress_track))
        
        print(exp_obj.id)
        session_v2.commit()
        
    session_v2.commit()


