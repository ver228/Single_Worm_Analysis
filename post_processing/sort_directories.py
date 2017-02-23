#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 20:34:51 2017

@author: ajaver
"""

import pymysql
import os

NONE_STR = '-N/A-'

def build_dir(row):
    if row['strain'] == '-N/A-':
        return ''
    
    if row['gene'] == NONE_STR:
            d_part1 = os.path.join('WT', row['strain'])
    else:
        dd = '{}@{}'.format(row['genotype'].replace(' ', ''), row['strain'])
        d_part1 = os.path.join('mutants', dd)
    
    if 'liquid' in row['arena'].lower():
        d_part2 = 'liquid'
    elif row['food'] == 'no food':
        d_part2 = row['food']
    else:
        d_part2 = 'food_' + row['food']
    d_part2 = d_part2.replace(' ', '_')
    
    if row['sex'] == 'hermaphrodite':
        d_part3 = 'XX'
    elif row['sex'] == 'male':
        d_part3 = 'XO'
        
    
    d_part4=row['habituation'].replace(' ', '_')
    
    d_parts = [d_part1, d_part2, d_part3, d_part4]
    
    return os.path.join(*d_parts)


def get_dir_from_base(base_name, cur=None):
    if cur is None:
        conn = pymysql.connect(host='localhost')
        cur = conn.cursor(pymysql.cursors.DictCursor)
        
        cur.execute('USE `single_worm_db`;')

    sql = '''
    SELECT base_name, date, strain, genotype, allele, gene, 
    chromosome, sex, food, habituation, arena
    FROM experiments_full
    WHERE base_name={}
    '''.format(base_name)

    cur.execute(sql)
    results = cur.fetchall()

    assert len(results) == 1
    return _build_dir(results[0])


