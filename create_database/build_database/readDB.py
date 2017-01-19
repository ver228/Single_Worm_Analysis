# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 16:27:04 2016

@author: ajaver
"""
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session



class SWDB:
    def __init__(self, db_name= r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2'):
        self.db_name = db_name
        self.engine = create_engine(db_name)
        self.Base = automap_base()
        self.Base.prepare(self.engine, reflect=True)
        
        self.c = {}
        for name, obj in self.Base.classes.items():
            self.c[name] = obj
            
        self.session = Session(self.engine)
    
    def _obj2col(self, obj, ignore_id=True, add_name=True):
        cols_names = [c.name for c in obj.__table__.columns]
        if ignore_id:
            cols_names = [c for c in cols_names if not 'id' in c]
        
        columns = [getattr(obj, c) for c in cols_names]
        
        if add_name:
            t_name = obj.__table__.name
            columns = [c if c.name != 'name' else c.label(t_name) 
            for c in columns]
        
        return columns
        
        
    def _get_query(self, base_table, tables2join, ignore_id=True, add_name=True):
        objs = []
        cols = self._obj2col(self.c[base_table], ignore_id, add_name)
        
        for name in  tables2join:
            obj = self.c[name]
            objs.append(obj)
            cols +=self._obj2col(obj, ignore_id, add_name)
        
        q = self.session.query(*cols)
        
        for obj in objs:
            q = q.join(obj)
        
        return q
    
    def read_table(self, base_table, tables2join='', ignore_id=False, add_name=False):
        
        query = self._get_query(base_table, tables2join, ignore_id, add_name)
        df = pd.DataFrame(query.all())
        return df


    def get_progress(self):
        tables2join = ['progress_masks', 'progress_tracks', 'exit_flags']
        base_table = 'experiments'
        
        return self.read_table(base_table, tables2join, ignore_id=True, add_name=True)
    
    def get_experiments(self):
        tables2join = ['strains', 'trackers', 'sexes',
       'developmental_stages', 'ventral_sides', 'foods', 'arenas',
       'habituations', 'experimenters', 'genes', 'alleles']
        
        base_table = 'experiments'
        
        return self.read_table(base_table, tables2join, ignore_id=True, add_name=True)
    
    def get_segworm_comp(self):
        tables2join = ['experiments', 'segworm_feature', 'progress_tracks']
        base_table = 'segworm_comparisons'
        return self.read_table(base_table, tables2join, ignore_id=True, add_name=True)

#%%
if __name__ == '__main__':
    swdb = SWDB()
    #tt = swdb.read_table('experiments')
    t2 = swdb.get_experiments()
    t3 = swdb.get_progress()
    #t4 = swdb.get_segworm_comp()
    
