#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 12:26:03 2017

@author: ajaver
"""

import pymysql

conn = pymysql.connect(host='localhost', db = 'single_worm_db')
cur = conn.cursor()

new_strains_data = '''
flp-10(pk367)	 NY133	 flp-10(pk367) (backcrossed x5)	 flp-10	 pk367	 IV
flp-12(n4092)	 NY106	 flp-12(n4092)(backcrossed x7)	 flp-12	 n4092	 -N/A-
flp-13(tm2448)	 NY244	 flp-13(NY244)(backcrossed x3)	 flp-13	 tm2448	 IV
flp-15(gk1186)	 NY249	 flp-15(gk1186)(backcrossed x3)	 flp-15	 gk1186	 III
flp-16(ok3085)	 RB2275	 flp-16(ok3085)	 flp-16	 ok3085	 II
flp-18(gk3063)	 NY245	 flp-18(gk3063)(backcrossed x3)	 flp-18	 gk3063	 X
flp-19(pk1594)	 NY193	 flp-19(pk1594)(backcrossed x6)	 flp-19	 pk1594	 -N/A-
flp-20(pk1596)	 NY184	 flp-20(pk1596)(backcrossed x7)	 flp-20	 pk1596	 X
flp-25(gk1016)	 NY230	 flp-25(gk1016)(backcrossed x2)	 flp-25	 gk1016	 X
flp-28(gk1075)	 NY248	 flp-28(gk1075)(backcrossed x3)	 flp-28	 gk1075	 X
flp-3(pk361)	 NY32	 flp-3(pk361)(backcrossed x8)	 flp-3	 pk361	 X
flp-14(gk1055)	 NY247	 flp-14(gk1055)(backcrossed x3)	 flp-14	 gk1055	 III
flp-4(yn35)	 NY119	 flp-4(yn35)	 flp-4	 yn35	 II
flp-4(yn35,ynIs99)	 NY2099	 flp-4(yn35,ynIs99)	 flp-4	 yn35;ynIs99	 II
flp-6(pk1593)	 NY183	 flp-6(pk1593)(backcrossed x7)	 flp-6	 pk1593	 -N/A-
flp-7(yn37)	 NY228	 flp-7(yn37)(backcrossed x3)	 flp-7	 yn37	 -N/A-
flp-9(yn36)	 NY227	 flp-9(yn36)(backcrossed x2)	 flp-9	 yn36	 -N/A-
yn8(pk360)	 NY34	 yn8(pk360)	 yn8	 pk360	 X
flp-1(ok2811)	 RB2126	 flp-1(ok2811)	 flp-1	 ok2811	 IV
'''


dd = [[y.strip() for y in x.split('\t')] for x in new_strains_data.split('\n') if x]
strains_data = {x[0]:x[1:] for x in dd}


if False:
    strains, descriptions, genes, alleles, chromosomes = map(set, zip(*strains_data.values()))
    
    for gene in genes:
        sql = '''
        INSERT IGNORE INTO genes
        SET name="{}";
        '''.format(gene)
        cur.execute(sql)
    
    for allele in alleles:
        sql = '''
        INSERT IGNORE INTO alleles
        SET name="{}";
        '''.format(allele)
        cur.execute(sql)
    
    for chromosome in chromosomes:
        sql = '''
        INSERT IGNORE INTO chromosomes
        SET name="{}";
        '''.format(chromosome)
        cur.execute(sql)
    
    
    for row in strains_data.values():
        sql = '''
        SELECT id
        FROM genes
        WHERE name="{}"
        '''.format(row[2])
        cur.execute(sql)
        gene_id, = cur.fetchone()
        
        sql = '''
        SELECT id
        FROM alleles
        WHERE name="{}"
        '''.format(row[3])
        cur.execute(sql)
        allele_id, = cur.fetchone()
        
        sql = '''
        SELECT id
        FROM chromosomes
        WHERE name="{}"
        '''.format(row[4])
        cur.execute(sql)
        chromosome_id, = cur.fetchone()
        
        row_i = (row[0], row[1], gene_id, allele_id, chromosome_id)
        sql = '''
        SET FOREIGN_KEY_CHECKS=0;
        REPLACE INTO strains
        SET name="{}",
        description="{}",
        gene_id={},
        allele_id={},
        chromosome_id={};
        SET FOREIGN_KEY_CHECKS=1;
        '''.format(*row_i)
        cur.execute(sql)
        
        print(sql)
    

#sql = '''
#select id, base_name 
#from experiments_full 
#where strain="-N/A-"
#and base_name like "%flp%";
#'''

sql = '''
select id, base_name 
from experiments_full 
where base_name like "%flp-16%";
'''

cur.execute(sql)
results = cur.fetchall()

str2replace = [
        ('flp-10(yu35)', 'flp-4(yu35)'),
        ('flp-(pk361)', 'flp-3(pk361)'),
        ('flp19', 'flp-19'),
        ('flp-7on', 'flp-7(yn37)on'),
        ('flp-9(yu36)', 'flp-9 (yn36)'),
        ('flp-4(yu355,yu1599)', 'flp-4(yn35,ynIs99)'),
        ('flp-4(yu35)', 'flp-4(yn35)'),
        ('flp-3(tm2448)', 'flp-13(tm2448)'),
        ('flp-9(yu86)', 'flp-9(yn36)'),
        ('flp-9(yu36)', 'flp-9(yn36)'),
        ('flp-1on', 'flp-1(ok2811)on'),
        ('flp-125', 'flp-25')
        ]

extra_str2replace = [
('flp-15(ko1963)', 'flp-15(gk1186)'),
('flp-18(ko1694)', 'flp-18(gk3063)'),
('flp-16(ok3985)', 'flp-16(ok3085)'),
('flp-20(pk1956)', 'flp-20(pk1596)'),
('flp-25(ko1646)', 'flp-25(gk1016)'),
('flp-25(ko1696)', 'flp-25(gk1016)'),
('flp-28(ko2121)', 'flp-28(gk1075)'),
('flp-4(ko1692)', 'flp-28(gk1075)')
]

str2replace += extra_str2replace


bad_ss = ['flp-97']

missing_bn = []
assigned_strains = []
weird_l = []
bad_strains = []
for irow, base_name in results:
    ss = base_name.replace(' ', '').lower()
    for old_s, new_s in str2replace:
        ss = ss.replace(old_s, new_s)
    
    if any(x in ss for x in bad_ss):
        
        bad_strains.append((irow, base_name))
        continue
    
    valid_k = [x for x in strains_data.keys() if x in ss]
    
    if len(valid_k) == 1:
        k = valid_k[0]
        strain_name = strains_data[k][0]
        
        assigned_strains.append((irow, base_name, strain_name))
    elif not valid_k:
        prefix = ss.partition('on')[0]
        missing_bn.append((irow, base_name, prefix))
    else:
        print(ss)
        weird_l.append((irow, base_name, valid_k))
    
assert not weird_l

for bad in sorted(missing_bn, key=lambda x:x[1]):
    print(bad)

for x in sorted(list(set(x[-1] for x in missing_bn))):
    print(x)

#%%
from collections import Counter
print(Counter([x[-1] for x in assigned_strains]))


for id_row, base_name, strain_name in assigned_strains:
    sql = '''
    SELECT id
    FROM strains
    WHERE name="{}"
    '''.format(strain_name)
    
    cur.execute(sql)
    strain_id, = cur.fetchone()
    
    
    
    sql = '''
    UPDATE experiments
    SET strain_id={}
    WHERE id={}
    '''.format(strain_id, id_row)
    
    cur.execute(sql)
    print(base_name)
    print(sql)

conn.commit()

conn.close()
