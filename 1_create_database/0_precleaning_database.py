# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 23:23:09 2016

@author: ajaver
"""
import os
import re
import datetime
import csv

from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import Table
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, DateTime, distinct

ENG_OLD_PATH = r'mysql+pymysql://ajaver:@localhost/single_worm_old'
MOVIES_LIST_F = os.path.join('..', 'files_lists', 'single_worm.txt')
INS_STRAINS_F = 'ins strains.csv'
#%%
Base = declarative_base()

class DataFromNames(Base):
    __tablename__ = 'data_from_names'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    file_name = Column(String(200), unique=True, index=True)
    directory = Column(String(500))
    side_str = Column(String(10))
    date = Column(DateTime())
    tracker_str = Column(String(20))
    strain_str = Column(String(100))
    media_str = Column(String(40))

class ExperimentsFullNew(Base):
    __tablename__ = 'experiments_full_new'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    original_video_name = Column(String(200), unique=True, index=True)
    base_name = Column(String(200), unique=True, index=True)
    directory = Column(String(500))
    strain =Column(String(20))
    allele = Column(String(20))
    gene =Column(String(20))
    chromosome = Column(String(10))
    genotype = Column(String(200))
    tracker =Column(String(20))
    sex = Column(String(20))
    developmental_stage = Column(String(20))
    ventral_side = Column(String(20))
    food = Column(String(50))
    arena = Column(String(100))
    habituation = Column(String(50))
    date = Column(DateTime())
    experimenter = Column(String(100))

#%%
def get_file_parts():
    #%%
    with open(MOVIES_LIST_F, 'r') as fid:
        data = [os.path.split(x) for x in fid.read().split('\n') if x]
    
    #%%
    #do not include any file that has test in the name
    data = [(d,f) for d, f in data if not 'test' in f.lower()] 
    
    #do not include any file that has "old video" or "control experiments" in the directory path
    data = [(d,f) for d, f in data if not 'old video' in d.lower()]
    data = [(d,f) for d, f in data if not 'control exp' in d.lower()]
    directories, file_names = zip(*data)
    
    file_names = [x.rpartition('.avi')[0] for x in file_names]
    #%%
    #this is known extracrap after the L and R simbole
    STR_S = '(?P<left>.*?)(?P<side>(L|R)*((\+| |O|A|z|1|t| TINY)*_))(?P<date>\d{4}(_\d{2}){2}_(_\d{2}){2,3})(?P<tracker>(_{2,3}\d*)+)$'
    prog_part1 = re.compile(STR_S, re.M|re.I)
    STR_S2 = '(?P<strain>.*?)(?P<media>(((o?(n|m))|off|all) \w?oo\w?)|( on.*)|(s?wim.*)|(_onfood))([ _]*)'
    prog_part2 = re.compile(STR_S2, re.M|re.I)

#    file_name = 'N2 on food R _2010_05_20__11_13___3___1'
#    result = prog_part1.match(file_name)
#    print((result.group('left'), result.group('side'), 
#                  result.group('date'), result.group('tracker')))
#    result2 = prog_part2.match(result.group('left'))
#    print(result2.group('strain'), '|', result2.group('media'))
    #%%
    file_parts = []
    weird_names = []
    for file_name in file_names:
        result = prog_part1.match(file_name)
        if not result is None:
            file_parts.append((result.group('left'), result.group('side'), 
                  result.group('date'), result.group('tracker')))
        else:
            weird_names.append(file_name)
    
    
    left_str, side_str, date_str, tracker_str = zip(*file_parts)
    
    dates = [datetime.datetime(*[int(y) for y in x.split('_') if y]) for x in date_str]
    
    assert all(len(x)>=1 for x in side_str)
    #side_str = [x[0].upper() for x in side_str.strip()]
    
    left_parts = []
    weird_left = []
    for ii, l_str in enumerate(left_str):
        result = prog_part2.match(l_str)
        if not result is None:
            left_parts.append((result.group('strain'),result.group('media')))
        else:
            left_parts.append((l_str, ''))
            weird_left.append((l_str, file_names[ii]))
    #print(weird_left)
    strain_str, media_str  = zip(*left_parts)
    strain_str = [x.strip() for x in strain_str]

    return file_names, directories, side_str, dates, tracker_str, strain_str, media_str


def create_base_table(myengine, session):
    file_names, directories, side_str, date, \
    tracker_str, strain_str, media_str = get_file_parts()
    
    data2insert = [{d:dat[ii] for ii,d in enumerate(['file_name', 'directory', 
    'side_str', 'date', 'tracker_str', 'strain_str', 'media_str'])} \
    for dat in zip(file_names, directories, side_str, date, \
    tracker_str, strain_str, media_str)]
    
    DataFromNames.__table__.drop(myengine, checkfirst=True)
    DataFromNames.__table__.create(myengine, checkfirst=True)
    session.add_all([DataFromNames(**x)for x in data2insert])
    session.commit()
    
def get_experimenter(directory):
    d = directory.lower()
    if 'laura' in d:
        return 'Laura Grundy'
    if 'andre' in d:
        return 'Andre Brown'
    if 'robyn' in d or 'rb1546' in d: 
        return 'Robyn Branicky'
    if 'monika' in d:
        return 'Monika Leubner'
        
    return None

def get_tracker(directory):
    d = re.findall('/Tracker \d+/', directory, re.I)
    if len(d) == 1:
        return d[0].lower().replace('/', '').replace(' ', '_')
    else:
        return None

def get_ventral_side(side_str):
    #remove everything but L and R
    sub_str = re.sub('[^LRlr]', '', side_str).upper() 
    if sub_str == 'R':
        return'anticlockwise'
    elif sub_str == 'L':
        return 'clockwise'
    else:
        return None

def get_sex(base_name):
    if 'male' in base_name.lower():
        return 'male'
    else:
        return 'hermaphrodite'

def get_develp_stage(base_name, food_str):
    if 'PS312' in base_name:
        return 'young adult'
    elif 'dauer' in base_name and not 'dauer' in food_str:
        return 'dauer'
    elif 'L3' in base_name and not 'L3' in food_str:
        return 'L3'
    elif 'L4' in base_name  and not 'L4' in food_str:
        return 'L4'
    else:
        return 'young adult'

def get_habituation(base_name):
    if 'no wait' in base_name:
        return 'NONE'
    else:
        return '30 minutes'

def get_food_arena(media_str):
    SWIM_MATCH = re.compile('s?wim.*')
    ONFOOD_MATCH = re.compile('^_*((o?(n|m)|all)[ _]*?\w?oo\w?)|(on)$', re.I|re.M)
    FOOD2CHANGE = {'food':'OP50', 'N2-LL2':'N2-L2', 'N2_LL2':'N2-L2',
               'rb557':'RB557', 'rb2005':'RB2005', 
               'mec-4(u253)-L3':'mec-4-L3'}

    media_str = media_str.strip()
    if re.match(SWIM_MATCH, media_str):
        arena = 'NGM liquid drop + 35mm petri dish NGM agar low peptone'
        food = 'OP50'
    else:
        arena = '35mm petri dish NGM agar low peptone'
        if 'off food' in media_str:
            food = 'NONE'
        elif not media_str or re.match(ONFOOD_MATCH, media_str.strip()):
            food = 'OP50'
        else:
            DD = re.findall(r'on ?[/)/(,0-9a-z/-A-Z_]+', media_str, re.I)
            DD = [x[2:].strip() for x in DD]
            DD = [FOOD2CHANGE[x] if x in FOOD2CHANGE else x for x in DD]
            food = '+'.join(DD)
    
    return arena, food
#%%
def FIND_DUPLICATES():
    from MWTracker.compressVideos.getAdditionalData import hasAdditionalFiles
    all_dat = {}
    for key, dat in zip(base_names, directories):
        #if not os.path.exists(os.path.join(dat,key + '.avi')):
        #    continue
        
        if not key in all_dat:
            all_dat[key] = [dat]
        else:
            all_dat[key].append(dat)
    
    rep_bn = [x for x in all_dat if len(all_dat[x])>1]
    
    for x in rep_bn:
        print(x)
        for d in all_dat[x]:
            if hasAdditionalFiles(os.path.join(d,x + '.avi')):
                print(':D {}'.format(d))
            else:
                print(':( {}'.format(d))
        print('%%%%%%%%%%%%%')

#%%
if __name__ == '__main__':
    #%%
    
    myengine = create_engine(ENG_OLD_PATH)
    meta = MetaData()
    meta.reflect(bind=myengine, views=True)
    experiments_full = Table('exp_annotation_full', meta, autoload=True)
    experiments = Table('experiments', meta, autoload=True)
    session = Session(myengine)

    ExperimentsFullNew.__table__.drop(myengine, checkfirst=True)
    ExperimentsFullNew.__table__.create(myengine, checkfirst=True)

    base_names, directories, side_strs, dates, \
    tracker_strs, strain_strs, media_strs = get_file_parts()
    create_base_table(myengine, session)
    
    new_rows = []
    for ii, dat in enumerate(zip(*get_file_parts())):
        if ii % 1000 == 0:
            print(ii)
        
        base_name, directory, side_str, date, tracker_str, \
        strain_str, media_str = dat
        
        old_data = session.query(experiments_full).\
        filter(experiments_full.c.file_name == base_name).one_or_none()
        
        if old_data is None:
            experimenter = get_experimenter(directory);
            strain, gene, allele, chromosome, genotype = 5*[None]
            
            habituation = get_habituation(base_name)
            ventral_side = get_ventral_side(side_str)
            tracker = get_tracker(directory)
            sex = get_sex(base_name)
        else:
            _, base_name_old, strain, allele, gene, chromosome, tracker, \
            _, _, ventral_side, food_old, habituation, experimenter, \
            _, genotype, _ = old_data
            
        sex = get_sex(base_name)
        arena, food = get_food_arena(media_str)
        developmental_stage = get_develp_stage(base_name, food)
        
        #if food_old != food and not old_data is None:
        #    print('{} | {} |O-{} | {}'.format(base_name, media_str,food_old,food))
        
        original_video_name = base_name + '.avi'
        
        row = {'original_video_name':original_video_name, 'base_name':base_name, 
               'directory':directory, 'strain': strain, 'gene':gene, 'allele':allele, 
               'chromosome':chromosome, 'genotype':genotype, 'tracker':tracker, 
               'sex':sex, 'developmental_stage':developmental_stage, 
               'ventral_side':ventral_side, 'food':food, 'arena':arena, 
               'habituation':habituation, 'date':date, 'experimenter':experimenter}
        
        session.add(ExperimentsFullNew(**row))
        #new_rows.append(ExperimentsFullNew(**row))
    
    #session.add(new_rows)
    session.commit()
    #%%
    experimenters = session.query(distinct(ExperimentsFullNew.experimenter)).all()
    if (None,) in experimenters:
        #select rows with a None as experimenter
        bad_experimenters = session.query(ExperimentsFullNew).filter(ExperimentsFullNew.experimenter == None).all()
        for bexp in bad_experimenters:
            #check the other experimenters of videos in the same the folder
            dd = session.query(ExperimentsFullNew.experimenter).filter(ExperimentsFullNew.directory == bexp.directory).all()
            valid_experimenter = set(x[0] for x in dd if not x[0] is None);
            #if there is only one experiment in the same folder we know the correct experiment
            if len(valid_experimenter) == 1:
                bexp.experimenter = valid_experimenter.pop()
    #%%
    #dd = session.query(distinct(ExperimentsFullNew.tracker)).all()
    bad_trackers = session.query(ExperimentsFullNew).\
    filter(ExperimentsFullNew.tracker == None).all()
    for btr in bad_trackers:
        dd = session.query(DataFromNames.tracker_str).\
        filter(DataFromNames.directory == btr.directory).all()
        
        STR_S3 = re.compile('_{2,3}\d*')
        MM = [re.findall(STR_S3, x[0])[0].replace('_', '') for x in dd]
        MM = set(MM)
        if len(MM) == 1:
            btr.tracker = 'tracker_' + MM.pop()
    #%%
    #dd = session.query(ExperimentsFullNew.base_name).\
    #filter(ExperimentsFullNew.food is None).all()
    dd = session.query(ExperimentsFullNew.food, DataFromNames.media_str).\
    join(DataFromNames, \
    ExperimentsFullNew.base_name==DataFromNames.file_name).all()
    set([x[0] for x in dd])
    #%%
    new_genes = {}
    new_allele = {}
    
    with open(INS_STRAINS_F, 'r') as fid:
        reader = csv.DictReader(fid)
        for row in reader:
            new_genes[row['Gene']] = (row['allele'], row['single mutant strain'])
            new_allele[row['allele']] = (row['Gene'], row['single mutant strain'])

    #laura_p2_strains = session.query(ExperimentsFullNew).\
    #filter(ExperimentsFullNew.genotype == None).\
    #filter(ExperimentsFullNew.directory.contains('Laura-phase2')).all()
    bad_strains = session.query(ExperimentsFullNew).\
    filter(ExperimentsFullNew.genotype == None).all()
    
    
    str2change = {
    'ins-33 (tm3608)' : 'ins-3 (tm3608)',
    'ins-13 (tm1875)' : 'ins-23 (tm1875)',
    'ins-21 (ok2474)' : 'ins-27 (ok2474)',
    'ins-ok2343)': 'ins-30 (ok2343)'
    }
    
    
    for p2_strain in bad_strains:#laura_p2_strains:
        strain_str = session.query(DataFromNames.strain_str).\
        filter(DataFromNames.file_name == p2_strain.base_name).one_or_none()[0]
        
        strain_str = strain_str.strip()
        if strain_str in str2change:
            strain_str =str2change[strain_str]
        
        
        d_match = re.match('^(?P<gene>ins-\d+|daf-28) \((?P<allele>.*?)\)?$', strain_str)
        
        if d_match is not None:
            gene = d_match.group('gene')
            a_str = d_match.group('allele')
            
           
            allele, strain = new_genes[gene]
            
            if (allele != a_str) and a_str in new_allele:
                if strain_str in str2change:
                    gene, allele, strain = str2change[strain_str]
                else:
                    gene2, strain2 = new_allele[a_str]
                    print('{} | {} {} | {} {}'.format(p2_strain.base_name, gene, allele, gene2, a_str))
                    continue
            
            p2_strain.gene = gene;
            p2_strain.allele = allele;
            p2_strain.strain = strain;
            p2_strain.genotype = '%s (%s)' % (gene, allele)
        elif 'ins' in strain_str:
            print('B', p2_strain.base_name) #show errors because the ins was not found
    session.commit()
    #%%
    #functions to check if a given allele/gene differs by how many characters from the expected allele/gene
    def char_diff(s1, s2):
        n_diff = 0
        if len(s1) != len(s2):
            return max(len(s1), len(s2))
        for c1, c2 in zip(s1, s2):
            if c1 != c2:
                n_diff += 1
        return n_diff
    
    def compare_diff(sets, ind2check, ori_str):
        s_diff = 10000
        best_s = []
        for s in sets:
            s_str = s[ind2check]
            new_diff = char_diff(ori_str, s_str)
            if new_diff < s_diff:
                best_s = [s]
                s_diff = new_diff
        return best_s, s_diff

    #%%
#    'PLG119': ['PLG 119 1', 'PLG 119 2', 'PLG119 1', 'PLG119 2', 'plg119'],
#    'PLG120':['PLG 120', 'PLG 120 1', 'PLG120 1', 'plg120', 'Plg120', 'PL;G120'],
    #all the miss_spelings I identified in the file names
    miss_spellings = {'Qt825 nca-1 nRHO-1 nNCA-1 Ex[acr-2 mcherry]': ['Qt825 nca-1 nRHO-1 nNCA-1 Ex [acr-2mcherry]',
    'Qt285 nca-1 nRHO-1 nNCA-1 Ex [acr-2 mcherry]', 'Qt285 nca-1 nRHO-1 nNCA-1 Ex [acr-2 mcherry]', 'Qt825 nca-1 nRHO-1 nNCA-1 Ex [acr-2 mcherry]',
    'Qt 825 nca-1 nRHO-1 nNCA-1 Ex [acr2 mcherry]', 'Qt825 nca-1 nRHO-1 n NCA-1 Ex[acr-2 mcherry]', 'QT825 nca-1 nRHO-1 nNCA-1 Ex [acr2mcherry]',
    'Qt825 nca-1 nRHO-1 nNCA-1Ex [acr-2mcherry]', 'Qt825 nca-1 nRHO-1 nNca-1 Ex[acr-2 mcherry]', 'Qt825 nca-1 nRHO-1 nNCA Ex [acr-2 mcherry]',
    'Qt825 nca-1 nRHO-1 nNCA-1 [acr-2 mcherry]'],
    'Br200':['br200'],
    'N2' : ['N2 L3', 'N2 male', 'N2_', 'N2 con', 'n2', '', 'N2 (Robyn)', 'Ne'],
    '507 ED3054':['507 ED3059', '07 ED3054', '507'],
    '532 CB4853':['532 CG4853', '532 CB4053'],
    '300 LSJ1':['300 LS51'],
    '422 ED3017':['422 JU3017'],
    '399 CB4856':['399 CB4956', '399 CB4586', '399 CB856'],
    '575 JU440':['575 Ju440'],
    '197 PS312':['197 PS323 3', '197 PS212 1', '197 PS3123 8','197 PS 312 2'],
    'Qt1084 unc-80 nRHO-1 nUNC-80 ttx GFP': ['qt1084 unc-80 nRHO-1 nUNC-80 ttx GFP',
    'Qt1084 unc-80 nRHO-1 nunc-80 ttx GFP', 'Qt1084 unc-80 nRHO-1 nUNC80 ttx GFP'],
    'pink-1 (tm1779)':['pink-1 (tm)'],
    'VC40429':['vc40429'],
    '14 JU393':['814 JU393'],
    'tsp-17(tm5169)':['tsp-17 (tm51)', 'tsp017(tm5169)', 'tsp-17(tm5168)','tsp-17(tm5160)'],
    'tsp-17(tm4995)':['tsp-17(tm1995)', 'tsp-17 (tm4995)', 'tsp-17 (tm4994)'],
    'tsp-17(gt1681)':['tsp-17(gt1686)', 'tsp-17(tmgt1681)', 'tsp-17(gt1868)',
     'tsp-17(g1681)', 'tsp-17(gt1691)', 'tsp-17 (gt1681)'],
    'unc-73 (lf)':['unc-73 (gf)', 'unc-73'],
    'tcht-1':['tcht-1-1', 'tcht-', 'tcht'],
    'pdr-1(gk448)':['pdr-17(gk448)', 'pdr-1', 'pdr-1(gk448))'],
    'nca-1 (gf)':['nca-1(gf)'],
    'lrk-1 (tm1898)':['lrk-1','lrk-1(1898)', 'lrk-1(tm1898)', 'lrt-1'],
    'ethc-1':['ethc-1-1','etch-1'],
    'flp-3(ok3265)':['flp-3 (ok3263)'],
    'flp-3 (pk361)':['flp- (pk361)'],
    'flp-4 (ko1692)':['flp-4  (ko1692)'],
    'flp-4 (yu355,yu1599)':['flp-4 (yu355, yu1599)', 'flp-4 (yu355, yu1599))'],
    'flp-4 (yu35)':['flp-4 (YU35)'],
    'flp-6 (pk1593)':['flp-6 (PK1593)','flp-6 (pk1593))'],
    'flp-13 (tm2448)':['lp-13 (tm2448)', 'flp-3 (tm2448)'],
    'flp-13 (tm2427)':['flp-113 (tm2427)'],
    'flp-19 (pk1594)':['flp19 (pk1594)'],
    'flp-20 (pk1596)':['flp-20 (pk1956)', 'flp-20 (PK1596)'],
    'flp-25 (ko1696)':['flp-125 (ko1696)', 'flp-25 (ko1646)'],
    'mec-10 (fm1552) mec-4 (u253)':['mec-10 (fm1552) mec-4 (u253) 1',
    'mec-10 (fm1552) mec-4 (u253) 2', 'mec-10 (fm1552) mec-4 (u253) 3',
    'mec-10 (fm1552) mec-4 (u253) 4', 'mec-10 (fm1552) mec-4 (u253) 8'],
    'mec-12 (u76)' : ['mec-7 (u76)'],
    'egl-17 (e1313)X':['egl-13 (e1313)X'],
    'egl-42 (n995)':['egl-42 (n995sd)'],
    'gpa-1 (pk15)V':['gpa-1 (pk35)V'],
    'trp-2 (gk298)':['trp-2 (ok298)'],
    'unc-10 (md1117)':['unc-10 (ad1117)'],
    'unc-73 (lf) nca-1 (gf)':['nca-1 (gf) unc-73 (gf)', 'unc-73 (gf) nca-1 (gf)', 
    'nca-1 (gf) unc-73 (lf)'],
    'tm1264':['TM1264'],
    'pcrg-1':['pgrc-1'],
    'Pocr-4 egl-1':['ocr-4 egl-1', 'pocr-4 egl-1'],

    'RB2005':['RB2005 1', 'RB20057'],
    'RB2005 cameleon IL2' : ['RB2005 cam IL2 2', 'RB2005 cameleon IL2 2'],
    'RB557':['rb557'],
    'RB557 cameleon IL2': ['RB557 IL2 cam 1', 'RB557 cam IL2 1', 'RB557 cameleon IL2 3'],

    'IL2 cam in RB557' : ['IL2 cam in RB557 1', 'IL2 cam RB557', 'il2 CAM IN rb557'],
    'IL2 cam in RB2005': ['IL2 cam IN RB2005', 'IL2 cam RB2005'],

    'PLG119 in RB557' :['PLG119 1 in RB557', 'PLG119 2 in RB557', 'PLG119 IN RB557 1',
    'PLG119 IN rb557 1', 'PLG119 IN rb557 2',  'PLG119 in RB557 1', 'plg119 in RB557 1',
    'PLG119 in RB557 2', 'PLG119 in RB5571', 'plg119 IN rb557 2', 'plg119 in RB557 2'],
    
    'PLG119 in RB2005': ['PLG 119 1 in rb2005', 'PLG 119 2 in rb2005', 'PLG119 in RB2005 1'],
    
    'PLG120 in RB2005' : ['PLG120 1 in RB2005', 'PLG120 1 in RB2005 1', 'PLG120 RB2005',
    'PLG120 in RB2005 1', 'PLG120 in RB2005 2', 'Plg120 in RB2005 2', 'PLG 120 in RB2005 1',
    'PL;G120 in RB2005', 'PLG 120 1 IN rb2005', 'PLG120 RB2005 2', 'plg120 in RB2005 1',
    'plg120 in RB2005 2'],

    '342.2 in RB2005':['342.2 inRB2005'],
    'LR342.2 in RB2005':['lr342.2 in RB2005', 'LR342.2 in RB2005 2', 'plg342.2 IN rb2005'],
    'ocr4;ocr2;ocr1' : ['LX982'],
    'ocr-2;4' : ['LX981']

    }

    str2change = {'unc-8':'unc-80 (e1069)', 
    'ocr-3 (ok1557)':'ocr-3 (ok1559)', 
    'AQ2000':'egl-42 (n995)',
    'AQ2458':'clh-3(ok768)II',
    'AQ63':'unc-36(e873)III',
    'AQ1062':'clh-3(ok763)',
    't28f2.7 (ok2657)I':'acd-5 (ok2657)I',
    't28f4.2 (ok289)I':'asic-2 (ok289)I',
    'acr-13or lev-8 (x15)X	':'lev-8 (x15)',
    'acr-20 (dpy20)':'acr-20(ok1849)/mT1 II; +/mT1 [dpy-10(e128)] III',
    'cr-3 (ok1557)':'ocr-3 (ok1559)',
    'MI24':'egl-21 (n611)IV',
    'T28F2.7 (ok2657)I':'acd-5 (ok2657)I',
    'unc-10 (ok1781)X':'egg-5 (ok1781)',
    'unc-7 (cb5)':'unc-7 (e5)',
    'trpa-1 (ok999); osm-9 (ky10)':'AQ1422',
    'acr-13or lev-8 (x15)X' : 'lev-8 (x15)X',
    'cf2027 Q40; def-2 (e1570)':'CF2027 Q40; def-2 (e1570)'
    }
    for key in miss_spellings:
        for bad_s in miss_spellings[key]:
            str2change[bad_s] = key
    #%%
    new_strains_dat = {
    'N2':('N2', None, None, None, 'Schafer Lab N2 (Bristol, UK)'),
    'JU343':('JU343', None, None, None, 'C. elegans wild isolate (Merlet, France)'),
    'AQ3000':('AQ3000', None, None,None, 'Queelim Lab N2 (Bristol, UK)'),
    'VC40429':('VC40429', None, None,None, 'Million Mutation Project strain'),
    'AQ2613':('AQ2613',None, None, None, 'ljEx337[podr-1::Cx36*::YFP, punc-122::mCherry]; ljEx336[pttx-3(int2)::Cx36*::mCherry, pelt-2::mCherry]'),
    ('pink-1', 'tm1779'):('BR4006', 'tm1779', 'pink-1' ,'II', 'pink-1(tm1779) II; byEx655'),
    ('pdr-1', 'gk448'):('VC1024', 'gk448', 'pdr-1','III', 'pdr-1(gk448) III'),
    }
    #%%
    genotype_query = session.query(experiments_full.c.strain, experiments_full.c.allele,
                              experiments_full.c.gene, experiments_full.c.chromosome,
                              experiments_full.c.genotype).\
                              distinct(experiments_full.c.strain, experiments_full.c.allele,
                              experiments_full.c.gene, experiments_full.c.chromosome,
                              experiments_full.c.genotype)
    #%%

    problem_strains = []
    problem_base_names = []
    
    bad_strains = session.query(ExperimentsFullNew).\
    filter(ExperimentsFullNew.genotype == None).all()
    for bad_strain in bad_strains:
        
        set_genotype = []
        
        strain_str = session.query(DataFromNames.strain_str).\
        filter(DataFromNames.file_name == bad_strain.base_name).one_or_none()[0]
        if strain_str in str2change:
            strain_str =str2change[strain_str]
        #%%
        strain_match = re.match('(\d{2,4} )?(?P<strain>[\-A-Z0-9;a-z]+)( .)?$', strain_str)
        genotype_match = re.match('^(?P<gene>[a-zA-Z\-0-9]+) ?\((?P<allele>[a-zA-Z\-0-9]*?)\)[IXV]{,3}$', strain_str)
        
        if strain_match:
            strain = strain_match.group('strain')
            
            if strain in new_strains_dat:
                set_genotype = [new_strains_dat[strain]]
            else:
                set_genotype = genotype_query.\
                filter(experiments_full.c.strain==strain).all()
        
        elif genotype_match:
                gene = genotype_match.group('gene').lower()
                allele = genotype_match.group('allele').lower()
                
                if (gene, allele) in new_strains_dat:
                    set_genotype = [new_strains_dat[(gene, allele)]]
                else:
                    set_genotype = genotype_query.\
                    filter(experiments_full.c.gene==gene).\
                    filter(experiments_full.c.allele==allele).\
                    all()
                
                    if len(set_genotype) == 0:
                        
                        #look for genes and compare and check the difference with the closest match allele
                        set_genes = genotype_query.\
                        filter(experiments_full.c.gene==gene).\
                        all()
                        set_gene, a_diff = compare_diff(set_genes, 1, allele)
    
                        #look for alleles and compare and check the difference with the closest match genes
                        set_alleles = genotype_query.\
                        filter(experiments_full.c.allele==allele).\
                        all()
                        set_allele, g_diff = compare_diff(set_alleles, 2, gene)
                        
                        if  a_diff == 1 and g_diff != 1:
                            genotype = set_gene
                        
                        elif g_diff == 1 and a_diff != 1:
                            genotype = set_allele
        #%%
        if len(set_genotype) == 1:
            dat = set_genotype[0]
            bad_strain.strain, bad_strain.allele, bad_strain.gene, \
            bad_strain.chromosome, bad_strain.genotype = dat
        else:
            problem_strains.append(strain_str)
            problem_base_names.append(bad_strain.base_name)
    #%%
    session.query(ExperimentsFullNew).filter(ExperimentsFullNew.allele =='-N/A-').update({'allele': None})
    session.query(ExperimentsFullNew).filter(ExperimentsFullNew.gene =='-N/A-').update({'gene': None})
    session.query(ExperimentsFullNew).filter(ExperimentsFullNew.chromosome =='-N/A-').update({'chromosome': None})
    session.query(ExperimentsFullNew).filter(ExperimentsFullNew.ventral_side =='unknown').update({'ventral_side': None})
    session.query(ExperimentsFullNew).filter(ExperimentsFullNew.habituation =='none').update({'habituation': 'NONE'})
    #%%
    
    session.commit()
    session.close()
    #%%
    from collections import Counter
    print('%%%%%%%%%%%')
    DD = Counter(problem_strains).most_common()
    for dd in sorted(DD):
        print(dd)
    #%%
    group_base_names = {}
    for strain, base_name in zip(*(problem_strains, problem_base_names)):
        if not strain in group_base_names:
            group_base_names[strain] = []
        group_base_names[strain].append(base_name)
    #%%
    range_base_names = {}
    
    for strain in group_base_names:
        base_n = group_base_names[strain]
        if len(base_n) > 1:
            DD = [re.findall('(?P<date>\d{4}(_\d{2}){2}_(_\d{2}){2,3})', x)[0][0] for x in base_n]
            range_base_names[strain] = '%s || %s' % (min(DD), max(DD))
        else:
            range_base_names[strain] = base_n[0]
    #%%
#    with open('problematic_strains.csv', 'w') as fid:
#        for strain in range_base_names:
#            fid.write('%s, %s\n' % (strain, range_base_names[strain]))
    #%%
#    ins_bad = [x for x in problem_base_names  if 'ins-' in x]
#    all_ins = session.query(ExperimentsFullNew.base_name, 
#                            ExperimentsFullNew.directory, ExperimentsFullNew.date).\
#                  filter(ExperimentsFullNew.base_name.contains('ins-')).all()
#    tt_all = [np.datetime64(x[-1]) for x in all_ins]
#    tt_bad = [(ii,np.datetime64(x[-1])) for ii, x in enumerate(all_ins) 
#    if x[0] in ins_bad and not 'Laura-phase2' in x[1]]
#    tt_bad = list(zip(*tt_bad))
#    #%%
#    plt.figure()
#    plt.plot(tt_all, '.')
#    plt.plot(tt_bad[0], tt_bad[1], 'or')


