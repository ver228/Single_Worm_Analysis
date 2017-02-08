# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 08:52:54 2016

@author: ajaver
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import distinct
from sqlalchemy.schema import Table
from sqlalchemy.orm import Session
#import os

from tables_definitions import Allele, Gene, Strain, Tracker, Sex, \
DevelopmentalStage, VentralSide, Food, Arena, Habituation, Experimenter, \
Experiment, ExitFlag, AnalysisProgress

#%%
if __name__ == '__main__':
    DROP_PREV_TABLES = False
    
    engine_old = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_old')
    engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db')
    
    all_tables = [Allele, Gene, Strain, Tracker, Sex, DevelopmentalStage, 
                  VentralSide, Food, Arena, Habituation, Experimenter, 
                  Strain, ExitFlag, AnalysisProgress, Experiment]
    #%%
    if DROP_PREV_TABLES:
        #drop all the previous existing tables. Start from black
        for new_table in all_tables[::-1]:
            new_table.__table__.drop(engine_v2, checkfirst=True)
    
    #intialize tables if they do not exists previously
    for new_table in all_tables:
        new_table.__table__.create(engine_v2, checkfirst=True)
    #%%
    
    
    meta = MetaData()
    meta.reflect(bind = engine_old, views=True)
    experiments_full_new =Table('experiments_full_new', meta, autoload=True)
    
    Base = automap_base()
    Base.prepare(engine_v2, reflect=True)
    
    #%%
    session_old = Session(engine_old)
    session_v2 = Session(engine_v2)
    #%%
    
#    singleTables = [('allele',Allele), ('gene',Gene), ('tracker',Tracker),('sex',Sex),
#     ('developmental_stage',DevelopmentalStage), ('ventral_side',VentralSide), 
#    ('food',Food),('arena',Arena), ('habituation',Habituation),('experimenter',Experimenter)]
#    
#    for old_col_str, obj_new in singleTables[::-1]:
#        dat = session_old.query(distinct(experiments_full_new.c[old_col_str])).all()
#        print(dat)
#        dat_obj = [obj_new(name = x) for x, in dat]
#        #session_v2.add_all(dat_obj)
#    
        
        #%%
    
#    session_old = Session(engine_old)
#    session_v2 = Session(engine_v2)
#    
#    meta_old = MetaData()
#    meta_old.reflect(bind = engine_old, views=True)
#    
#    meta_v2 = MetaData()
#    meta_v2.reflect(bind = engine_v2, views=True)
#    
#    
#    singleTables = [('alleles','allele'), 
#                    ('genes','gene'), 
#                    ('trackers','tracker'),
#                    ('sexes','sex'),
#                    ('developmental_stages', 'developmental_stage'), 
#                    ('ventral_sides', 'ventral_side'), 
#                    ('foods','food'),
#                    ('arenas', 'arena'), 
#                    ('habituations','habituation'),
#                    ('experimenters','experimenter')
#                    ]
#    experiments_full_new =Table('experiments_full_new', meta_old, autoload=True)
#    for new_table_name, old_col in singleTables:
#        values = session_old.query(distinct(experiments_full_new.c[old_col])).all()
#        new_table = Table(new_table_name, meta_v2, autoload=True)
#        ins = new_table.insert().values(name=values)
#        
#        print(new_table_name, values)
    #%%
#    def get_table_keys(Obj):
#        dat = session_v2.query(getattr(Obj, 'id'), getattr(Obj, 'name')).all()
#        return {n:i for i,n in dat}
#    #%%
#    #create strain to insert
#    dd = [experiments_full_new.c.strain, experiments_full_new.c.allele, 
#          experiments_full_new.c.gene, experiments_full_new.c.genotype]
#    strains = session_old.query(*dd).distinct(*dd).all()
#    
#    genes_d = get_table_keys(Gene)
#    alleles_d = get_table_keys(Allele)
#    
#    strains_k = [(s,alleles_d[a],genes_d[g],gt) for (s,a,g,gt) in strains]
#    #%%
#    strains_obj = [Strain(name=s, allele_id=a, gene_id=g, genotype=gt) for (s,a,g,gt) in strains_k]
#    session_v2.add_all(strains_obj)
#    
#    #%%
#    dd = [experiments_full_new.c.base_name, 
#          experiments_full_new.c.date, 
#          experiments_full_new.c.strain, experiments_full_new.c.tracker, 
#          experiments_full_new.c.sex, experiments_full_new.c.developmental_stage, 
#          experiments_full_new.c.ventral_side,
#          experiments_full_new.c.food, experiments_full_new.c.arena, 
#          experiments_full_new.c.habituation, experiments_full_new.c.experimenter]
#    experiments = session_old.query(*dd).distinct(*dd).all()
#    
#    #%%
#    experiments_obj = []
#    exp_fields = ['base_name', 'date',
#                'strain_id', 'tracker_id', 'sex_id',
#                'developmental_stage_id', 'ventral_side_id', 'food_id','arena_id',
#                'habituation_id','experimenter_id']
#    
#    obj4keys = {'strain_id':Strain, 'tracker_id':Tracker, 'sex_id':Sex,
#                'developmental_stage_id':DevelopmentalStage, 'ventral_side_id':VentralSide,
#                'food_id':Food, 'arena_id':Arena, 'habituation_id':Habituation,
#                'experimenter_id':Experimenter}
#    dict4keys = {x:get_table_keys(obj4keys[x]) for x in obj4keys}
#    #%%
#    exp_rows = []
#    for exp_dat in experiments:
#        exp_dict = {}
#        for ii, key in enumerate(exp_fields):
#            if key in obj4keys:
#                id_dict = dict4keys[key]
#                exp_dict[key] = id_dict[exp_dat[ii]]
#            else:
#                exp_dict[key] = exp_dat[ii]
#        
#        exp_rows.append(Experiment(**exp_dict))
#       
#    session_v2.add_all(exp_rows)
#    session_v2.commit()
#    #%% Let's add the fields from the original videos
#    dd = [experiments_full_new.c.base_name, experiments_full_new.c.directory]
#    base2dir = {x:d for x,d in session_old.query(*dd).distinct(*dd).all()}
#    
#    #%%
#    video_rows = []
#    for ii, exp in enumerate(exp_rows):
#        if ii % 100 == 0: 
#            print('Getting original video file size {}/{}'.format(ii,len(exp_rows)))
#        vid_dict = {'experiment_id':exp.id,
#        'directory':base2dir[exp.base_name], 
#        'name': exp.base_name + '.avi'}
#        
#        video_file = os.path.join(vid_dict['directory'], vid_dict['name'])
#        vid_dict['sizeMB'] = os.path.getsize(video_file)/(1024*1024.0)
#        
#        video_rows.append(OriginalVideo(**vid_dict))
#    session_v2.add_all(video_rows)
    #%%
    session_v2.commit()
