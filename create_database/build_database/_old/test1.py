# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 14:53:13 2016

@author: ajaver
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import Table
from sqlalchemy.orm import Session

#from sqlalchemy.orm import mapper, sessionmaker

myengine = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_old')

from sqlalchemy import inspect
inspector = inspect(myengine)

for table_name in inspector.get_table_names():
    print('TABLE: %s' % table_name)
    print([x['name'] for x in inspector.get_columns(table_name)])


useful_data = ['age', 'allele', 'avifilesize', 'chromosome', 'correctedvulvaside', 
'experimenterlocation', 'experimenters', 'food', 'gene', 'genotype', 
'habituation', 'sex', 'strain', 'trackerno', 'treatment', 'ventralside', 
'wormside']
['ambiguousstrainexperimentlist']

databases = ['exp_annotationdb', 'info']

#%%

meta = MetaData()
meta.reflect(bind=myengine, views=True)
experiments_full =Table('exp_annotation_full', meta, autoload=True)

session = Session(myengine)

dd = session.query(experiments_full).filter(experiments_full.c.id==3).one()

#%%
#from sqlalchemy.ext.automap import automap_base
#from sqlalchemy.schema import Table
#from sqlalchemy.orm import Session, joinedload, load_only
#from sqlalchemy import sql
#from sqlalchemy import func
#
## reflect the tables
##Base = automap_base()
##Base.prepare(myengine, reflect=True)
#
#Base = automap_base(metadata=meta)
#Base.prepare()
#
#
#ExpAnnotation = Base.classes.exp_annotation
#Experiments = Base.classes.experiments
#Strain = Base.classes.strain
#Allele = Base.classes.allele
#Gene = Base.classes.gene
#Chromosome = Base.classes.chromosome
#Tracker = Base.classes.trackerno
#Sex = Base.classes.sex
#Age = Base.classes.age
#VentralSide = Base.classes.ventralside
#Food = Base.classes.food
#Habituation = Base.classes.habituation
#ExperimenterLocation = Base.classes.experimenterlocation
#Experimenter = Base.classes.experimenters
#Genotype = Base.classes.genotype
#Treatment = Base.classes.treatment
#
#session = Session(myengine)
#
#q = session.query(Sex)
#for row in q.all():
#    print(row.sexName)
#    
##%%
#
##%%
#conn = myengine.connect()
##%%
#
#exps_query = session.query(ExpAnnotation.id, Experiments.wormFileName, \
#Strain.strainName, Allele.alleleName, Gene.geneName, Chromosome.chromosomeName,\
#Tracker.trackerName, Sex.sexName, Age.ageName, VentralSide.ventralSideName,
#Food.foodName, Habituation.habitName, Experimenter.name, Genotype.genotypeName,
#Treatment.treatmentName).\
#join(Experiments).\
#join(Strain).\
#join(Allele).\
#join(Gene).\
#join(Chromosome).\
#join(Tracker).\
#join(Sex).\
#join(Age).\
#join(VentralSide).\
#join(Food).\
#join(Habituation).\
#join(ExperimenterLocation).\
#join(Experimenter).\
#join(Genotype).\
#join(Treatment)



#dd = Table("exp_annotation_full", meta, autoload=True)



#results = exps_query.all()

#filter(Sex.sexID == Exp_annotationdb.sexID).\
#for row in result.all():
#    print(row)
#%%
#row = result.fetchone();
#for row in result:
#    print(row)

