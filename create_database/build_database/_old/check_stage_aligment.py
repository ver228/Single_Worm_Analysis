# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:17:35 2016

@author: ajaver
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

import os
import tables



def isBadStageAligment(skeletons_file):
    with tables.File(skeletons_file, 'r') as fid:
        try:
            good_aligment = fid.get_node('/stage_movement')._v_attrs['has_finished'][:]
        except (KeyError,IndexError, tables.exceptions.NoSuchNodeError):
            good_aligment = 0;
        
        return not good_aligment in [1,2]

if __name__ == '__main__':
    engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
    Base = automap_base()
    Base.prepare(engine_v2, reflect=True)
    Experiment = Base.classes.experiments
    OriginalVideo = Base.classes.original_videos
    
    session_v2 = Session(engine_v2)

    all_data = session_v2.query(Experiment.base_name, OriginalVideo.directory).\
    join(OriginalVideo).all()
    
    with open('stage_problems.txt', 'w') as fid:
        for ii_dat, (base_name, directory) in enumerate(all_data):
            results_dir = directory.replace('/thecus/', '/Results/')
            skeletons_file = os.path.join(results_dir, base_name + '_skeletons.hdf5')
            
        
            if os.path.exists(skeletons_file) and isBadStageAligment(skeletons_file):
                print(ii_dat)
                fid.write(skeletons_file + '\n')