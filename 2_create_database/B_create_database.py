#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 18:13:25 2017

@author: ajaver
"""

import pymysql.cursors
import os



SIMPLE_TABLES = [
    'alleles', 
    'genes',
    'chromosomes',
    'trackers', 
    'sexes', 
    'developmental_stages', 
    'ventral_sides',
    'foods',
    'arenas',
    'habituations',
    'experimenters']

def init_database(DROP_PREV_DB = False):
    # Connect to the database
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    #create if not exists new database
    if DROP_PREV_DB:
        print('Deleting previous database')
        cur.execute('DROP DATABASE IF EXISTS `single_worm_db`;')
    
    
    sql = "CREATE DATABASE IF NOT EXISTS `single_worm_db`;"
    cur.execute(sql)
    cur.execute('USE `single_worm_db`;')
    print('>>>>>>>>>>>')
    
    #create all tables
    simple_tab_sql_str = \
    '''
    CREATE TABLE IF NOT EXISTS `{}`
    (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(100) UNIQUE NOT NULL,
    PRIMARY KEY (id)
    );
    '''
    
    strains_tab_sql = '''
    CREATE TABLE IF NOT EXISTS `strains`
    (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(200),
    gene_id INT NOT NULL,
    allele_id INT NOT NULL,
    chromosome_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (gene_id) REFERENCES genes(id),
    FOREIGN KEY (allele_id) REFERENCES alleles(id)
    );
    '''
    
    experiment_tab_sql = '''
    CREATE TABLE IF NOT EXISTS `experiments`
    (
    `id` INT NOT NULL AUTO_INCREMENT,
    `base_name` VARCHAR(200) UNIQUE NOT NULL,
    `date` DATETIME,
    `strain_id` INT,
    `tracker_id` INT,
    `sex_id` INT,
    `developmental_stage_id` INT,
    `ventral_side_id` INT,
    `food_id` INT,
    `arena_id` INT,
    `habituation_id` INT,
    `experimenter_id` INT,
    `original_video` VARCHAR(700) NOT NULL UNIQUE,
    `original_video_sizeMB` FLOAT,
    `exit_flag_id` INT NOT NULL DEFAULT 0,
    `results_dir` VARCHAR(200),
    `youtube_id` VARCHAR(40),
    `zenodo_id` INT,
    
    INDEX (zenodo_id),
    PRIMARY KEY (id),
    FOREIGN KEY (strain_id) REFERENCES strains(id),
    FOREIGN KEY (tracker_id) REFERENCES trackers(id),
    FOREIGN KEY (sex_id) REFERENCES sexes(id),
    FOREIGN KEY (developmental_stage_id) REFERENCES developmental_stages(id),
    FOREIGN KEY (ventral_side_id) REFERENCES ventral_sides(id),
    FOREIGN KEY (food_id) REFERENCES foods(id),
    FOREIGN KEY (arena_id) REFERENCES arenas(id),
    FOREIGN KEY (habituation_id) REFERENCES habituations(id),
    FOREIGN KEY (experimenter_id) REFERENCES experimenters(id),
    FOREIGN KEY (exit_flag_id) REFERENCES exit_flags(id)
    )
    '''
    
    ##### progress table
    
    exit_flags_tab_sql = \
    '''
    CREATE TABLE IF NOT EXISTS `exit_flags`
    (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(30) UNIQUE NOT NULL,
    `description` VARCHAR(100),
    PRIMARY KEY (id)
    );
    '''
    #%%
    exit_flags_vals = [
    ('COMPRESS' , 'Create masked video.'), 
    ('COMPRESS_ADD_DATA', 'Add additional data to the video (stage and pixel size).'), 
    ('VID_SUBSAMPLE' , 'Create subsampled video.'), 
    ('TRAJ_CREATE', 'Create trajectories.'),
    ('TRAJ_JOIN', 'Join trajectories.'),  
    ('SKE_INIT' , 'Initialize trajectories table.'), 
    ('BLOB_FEATS', 'Get features from the segmented image.'),  
    ('SKE_CREATE', 'Create skeletons.'),  
    ('SKE_FILT', 'Filter skeletons.'), 
    ('SKE_ORIENT', 'Orient skeletons by movement.'),  
    ('STAGE_ALIGMENT', 'Stage aligment.'),  
    ('INT_PROFILE', 'Intensity profile.'),  
    ('INT_SKE_ORIENT', 'Orient skeletons by intensity.'),  
    ('FEAT_CREATE', 'Obtain features.'),
    ('WCON_EXPORT', 'Export data into WCON.'),
    ('END', 'Finished.'),  
    ]
    
    exit_flags_vals_failed = [
    (103, 'INVALID_VIDEO', 'Video cannot be read.'),
    (104, 'MISSING_ADD_FILES', 'The extra files log.csv and/or info.xml are missing.')
    ]
    
    exit_flags_init = ('INSERT INTO exit_flags (name, description) VALUES (%s, %s)',
                       exit_flags_vals)
    
    exit_flags_init_f = ('INSERT INTO exit_flags (id, name, description) VALUES (%s, %s, %s)',
                       exit_flags_vals_failed)
    
    #%%
    
    
    progress_analysis_tab_sql = \
    '''
    CREATE TABLE IF NOT EXISTS `results_summary`
    (
    `experiment_id` INT NOT NULL,
    `n_valid_frames` INT,
    `n_missing_frames` INT,
    `n_segmented_skeletons` INT,
    `n_filtered_skeletons` INT,
    `n_valid_skeletons` INT,
    `n_timestamps` INT,
    `first_skel_frame` INT,
    `last_skel_frame` INT,
    `fps` FLOAT,
    `total_time` FLOAT,
    `mask_file_sizeMB` FLOAT,
    `upload_size_MB` FLOAT,
    PRIMARY KEY (experiment_id),
    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
    );
    '''
    
    segworm_features_tab_sql = \
    '''
    CREATE TABLE IF NOT EXISTS `segworm_info`
    (
    `id` INT NOT NULL AUTO_INCREMENT,
    `segworm_file` VARCHAR(700),
    `experiment_id` INT NULL,
    `fps` FLOAT,
    `total_time` FLOAT,
    `n_segworm_skeletons` INT,
    `n_timestamps` INT,
    PRIMARY KEY (id),
    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
    )
    '''
    
    segworm_comparisons_tab_sql = \
    '''
    CREATE TABLE IF NOT EXISTS `segworm_comparisons`
    (
    `experiment_id` INT NOT NULL,
    `segworm_info_id` INT NOT NULL,
    `n_mutual_skeletons` INT,
    `n_switched_head_tail` INT,
    `error_05th` FLOAT,
    `error_50th` FLOAT,
    `error_95th` FLOAT,
    PRIMARY KEY (experiment_id),
    FOREIGN KEY (experiment_id) REFERENCES experiments(id),
    FOREIGN KEY (segworm_info_id) REFERENCES segworm_info(id)
    )
    '''
    
    
    #%%
    file_types_tab_sql = \
    '''
    CREATE TABLE IF NOT EXISTS `file_types`
    (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(20),
    `extension` VARCHAR(20),
    `description` VARCHAR(700),
    PRIMARY KEY (id),
    UNIQUE KEY (name),
    UNIQUE KEY (extension)
    )
    '''
    
    file_types_vals = [
    ('masked_video', '.hdf5' , 'Video data stored in hdf5 with the background zeroed'), 
    ('features', '_features.hdf5', 'Worm skeletons and features.'), 
    ('wcon', '.wcon.zip', 'Metadata and skeletons saved in the tracker commons format (https://github.com/openworm/tracker-commons)'), 
    ('preview', '_subsample.avi', 'Subsampled video file used as a preview of the hdf5 video data.')
    ]
    
    file_types_init = ('INSERT INTO file_types (name, extension, description) VALUES (%s, %s, %s)',
                       file_types_vals)
    
    #%%
    file_types_tab_sql = \
    '''
    CREATE TABLE IF NOT EXISTS `zenodo_files`
    (
    `id`  VARCHAR(120),
    `zenodo_id` INT,
    `filename` VARCHAR(250),
    `filesize` BIGINT,
    `checksum` CHAR(32),
    `download_link` VARCHAR(2083),
    `file_type_id` INT,
    PRIMARY KEY (id),
    FOREIGN KEY (zenodo_id) REFERENCES experiments(zenodo_id) 
    ON DELETE CASCADE ON UPDATE CASCADE
    
    FOREIGN KEY  (file_type_id) REFERENCES file_types(id);
    );
    '''
    
    #%%
    
    all_tabs_sql = [strains_tab_sql,
    exit_flags_tab_sql,
    experiment_tab_sql,
    progress_analysis_tab_sql,
    segworm_features_tab_sql, 
    segworm_comparisons_tab_sql,
    file_types_tab_sql
    ]
    
    for s_tab in SIMPLE_TABLES:
        sql = simple_tab_sql_str.format(s_tab)
        print(sql)
        print('**********')
        cur.execute(simple_tab_sql_str.format(s_tab))
    
    for sql in all_tabs_sql:
        print(sql)
        print('**********')
        cur.execute(sql)
        conn.commit()
    
    print('Creating database')
    cur.executemany(*exit_flags_init)
    cur.executemany(*exit_flags_init_f)
    cur.executemany(*file_types_init)
    
    create_full_view_sql = '''
    CREATE OR REPLACE VIEW experiments_full AS
    SELECT 
    e.id AS id, 
    e.base_name AS base_name,
    e.date AS date, 
    e.original_video as original_video,
    e.original_video_sizeMB as original_video_sizeMB,
    e.results_dir  as results_dir,
    s.name AS strain,
    s.description AS strain_description,
    a.name AS allele, 
    g.name AS gene, 
    c.name AS chromosome, 
    t.name AS tracker, 
    sex.name AS sex, 
    ds.name AS developmental_stage, 
    vs.name AS ventral_side, 
    f.name AS food, 
    h.name AS habituation, 
    experimenters.name AS experimenter,
    arenas.name AS arena,
    exit_flags.name AS exit_flag
    
    FROM experiments AS e 
    LEFT JOIN strains AS s ON e.strain_id = s.id
    LEFT JOIN alleles AS a ON s.allele_id = a.id
    LEFT JOIN genes AS g ON s.gene_id = g.id
    LEFT JOIN chromosomes AS c ON s.chromosome_id = c.id
    LEFT JOIN trackers AS t ON e.tracker_id = t.id
    LEFT JOIN sexes AS sex ON e.sex_id = sex.id
    LEFT JOIN developmental_stages AS ds ON e.developmental_stage_id = ds.id
    LEFT JOIN ventral_sides AS vs ON e.ventral_side_id = vs.id
    LEFT JOIN foods AS f ON e.food_id = f.id
    LEFT JOIN habituations AS h ON e.habituation_id = h.id
    LEFT JOIN experimenters ON e.experimenter_id = experimenters.id
    LEFT JOIN arenas ON e.arena_id = arenas.id
    LEFT JOIN exit_flags ON e.exit_flag_id = exit_flags.id
    '''
    
    cur.execute(create_full_view_sql)
    
    '''
    CREATE OR REPLACE VIEW experiments_valid AS
    SELECT *
    FROM experiments_full
    JOIN results_summary ON id = experiment_id
    WHERE strain != '-N/A-'
    AND exit_flag = 'END'
    AND n_valid_skeletons>100 
    AND total_time < 100000
    '''
    
    
    cur.execute('SHOW TABLES')
    print(cur.fetchall())
    
    cur.close()
    conn.close()

    
def fill_table(REPLACE_DUPLICATES = True):
    # Connect to the database
    conn = pymysql.connect(host='localhost')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    #load all database
    cur.execute('USE `single_worm_old`;')
    cur.execute('SELECT * FROM experiments_full_new;')
    full_data = cur.fetchall()
    cur.execute('USE `single_worm_db`;')
    
    
    def _get_single_name(x):
        return  x[:-1] if x != 'sexes' else 'sex'
    
    for tab_name in SIMPLE_TABLES:
        single_name = _get_single_name(tab_name)
        print(single_name)
        print(full_data[0])
        dat = sorted(set(x[single_name] for x in full_data))
        
        if 'ventral_side':
            print(dat)
        init_str = 'INSERT INTO {} (name) VALUES (%s)'.format(tab_name)
        if REPLACE_DUPLICATES:
            init_str += ' ON DUPLICATE KEY UPDATE name=name;'
        cur.executemany(init_str, dat)
    conn.commit()
    
    #get simple tables ids
    def _get_id_dict(tab_name):
        cur.execute('SELECT id, name FROM {}'.format(tab_name))
        tab = cur.fetchall()
        return {x['name']:x['id'] for x in tab}
                
    all_dict = {}
    for tab_name in SIMPLE_TABLES:
        
        single_name = _get_single_name(tab_name)
        
        all_dict[single_name] = _get_id_dict(tab_name)
        print(tab_name, single_name)
    
    print(SIMPLE_TABLES)
    print(all_dict['ventral_side'])
    
    # add strains list
    def fk2(x):
        DD =  ['gene', 'allele', 'chromosome']
        output = tuple([x['strain'], x['genotype']] +  [all_dict[fn][x[fn]] for fn in DD])
        return output
    
    
    print('Reading all data')
    strains_dat = set([fk2(x) for x in full_data])
    strains_init = '''
    INSERT INTO strains (name, genotype, gene_id, allele_id, chromosome_id) 
    VALUES (%s, %s, %s, %s, %s)'''
    if REPLACE_DUPLICATES:
        strains_init += ' ON DUPLICATE KEY UPDATE genotype=genotype, name=name, gene_id=gene_id, allele_id=allele_id, chromosome_id=chromosome_id;'''
    
    cur.executemany(strains_init, strains_dat)
    conn.commit()
    
    
    tab_name = 'strains'
    single_name = _get_single_name(tab_name)
    all_dict[single_name] = _get_id_dict(tab_name)
    
    # add strains list
    def fk2exp(x):
        col_ids =  ['strain', 
                   'tracker', 
                   'sex', 
                   'developmental_stage', 
                   'ventral_side',
                   'food',
                   'arena',
                   'habituation',
                   'experimenter']
        
        cols = ['base_name', 
                'date']
        
        output1 = [x[fn] for fn in cols]
        ori_dir = [os.path.join(x['directory'], x['original_video_name'])]
        output2 = [all_dict[fn][x[fn]] for fn in col_ids]
        output = tuple(output1 + ori_dir + output2)
        
        return output
    
    exp_dat = [fk2exp(x) for x in full_data]
    
    exp_init = '''
    INSERT INTO experiments (base_name, date, original_video, 
    strain_id, tracker_id, sex_id, developmental_stage_id, 
    ventral_side_id, food_id, arena_id, habituation_id, experimenter_id, exit_flag_id) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
    '''
    
    if REPLACE_DUPLICATES:
        exp_init += ''' 
        ON DUPLICATE KEY UPDATE 
        base_name=base_name, 
        date=date,
        original_video=original_video,
        strain_id=strain_id, 
        tracker_id=tracker_id, 
        sex_id=sex_id,
        developmental_stage_id=developmental_stage_id, 
        ventral_side_id=ventral_side_id, 
        food_id=food_id,
        arena_id=arena_id, 
        habituation_id=habituation_id, 
        experimenter_id=experimenter_id,
        exit_flag_id=1;
        '''
    
    print('Inserting {} experiments'.format(len(exp_dat)))
    cur.executemany(exp_init, exp_dat)
    conn.commit()
    
    cur.close()
    conn.close()
    

def add_video_sizes():
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor()
    
    ori_vid_sql = 'SELECT id, original_video FROM experiments'
    cur.execute(ori_vid_sql)
    results = cur.fetchall()
    
    
    #video_sizes = []
    for ii, (vid_id, original_video) in enumerate(results):
        if ii % 100 == 0: 
            print('Getting original video file size {}/{}'.format(ii,len(results)))
        
        size = os.path.getsize(original_video)/(1024*1024.0)
        sql = '''UPDATE experiments  SET original_video_sizeMB={} WHERE id={}'''.format(size, vid_id)
        cur.execute(sql)
        
    conn.commit()
    
    cur.close()
    conn.close()
    
if __name__ == '__main__':
    DROP_PREV_DB = False
    REPLACE_DUPLICATES = False
    
    
    init_database(DROP_PREV_DB)
    fill_table(REPLACE_DUPLICATES)
    #add_video_sizes()
    