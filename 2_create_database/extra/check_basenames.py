#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  9 10:32:34 2017

@author: ajaver
"""

import pymysql


conn = pymysql.connect(host='localhost', database='single_worm_db')
cur = conn.cursor()


sql = '''
select s.name, g.name, base_name
from  experiments
join strains as s on s.id = strain_id
JOIN genes AS g ON g.id = gene_id
JOIN alleles AS a ON a.id = allele_id
where not base_name like CONCAT("%", s.name,"%")
and not base_name like CONCAT("%", g.name,"%")
and not base_name like CONCAT("%", a.name,"%")
and s.name != "-N/A-"
'''

cur.execute(sql)
results = cur.fetchall()

results = set([(x[0], x[1], x[2].rpartition(' ')[0]) for x in results])

for x in results:
    print(x)

'''
('RB1883', 'trpl-2', 'W03B1.2 (ko2433) on food')
('FX3085', 'trpa-2', 'M0585.6 (ok3085) on food')
('MT2068', 'egl-42', 'AQ2000 on food')
('VP91', 'clh-3', 'AQ1062 on food')
('CB101', 'unc-9', 'AQ31 on food')
('FX3085', 'trpa-2', 'M05B5.6 (ok3289) on food')
('AQ2936', 'nRHO-1;unc-80', 'unc-80 (e1069) nRHO-1 G14Von food')
('MT2068', 'egl-42', 'AQ200L on food')
('VC12', 'unc-77', 'C11D2.6 (gk29)IV on food')
('MT15434', 'tph-1', 'superoutcrossed on food')
('MT13292', 'mir-124', 'M124 on food')
('RB1818', 'del-4', 'C1B2.6 (ko2353) on food')
('RB905', 'clh-3', 'AQ2458 on food')
('RB1958', 'npr-20', 'T07D4.1 (ok255)II on food')


('N2', '-N/A-', 'dop-1 (vs101)X on food')
('N2', '-N/A-', 'dop-3 (vs106)X on food')
('N2', '-N/A-', 'dop-2;dop-3 on food')
('N2', '-N/A-', 'dop-2 (vs103)V on food')
('N2', '-N/A-', 'cat-2 (e112) on food')
'''
