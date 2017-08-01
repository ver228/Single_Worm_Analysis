#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:46:03 2017

@author: ajaver
"""
import pymysql
import os
import sys
import requests
sys.path.append('../2_create_database')
from helper.db_info import db_row2dict

valid_ext = ['_skeletons.hdf5', 
             '_features.hdf5',
             '_subsample.avi', 
             '.wcon.zip', 
             '.hdf5']

#import sys
#import os
#import urllib
#
## We must add .. to the path so that we can perform the
## import of open-worm-analysis-toolbox while running this as
## a top-level script (i.e. with __name__ = '__main__')
#sys.path.append('..')
#
#from zenodio.deposition import Deposition
#
#ACCESS_TOKEN  = 'n2vW3bQz2mVHzGL3KiSrVZzqtAv8Wv3kGE3fOdfkXTlxFserY47r9TASG1Hx'
#
#book_path = 'WealthOfNations.pdf'
#urllib.request.urlretrieve(
#    "http://www.ibiblio.org/ml/libri/s/SmithA_WealthNations_p.pdf",
#    book_path)
#
#book_metadata = {"metadata": {
#    "title": "An Inquiry into the Nature and Causes of the Wealth of Nations",
#    "upload_type": "publication",
#    "publication_type": "book",
## Note: due to a Zenodo bug we cannot use a date prior to 1900, so we cannot
## use the correct publication data of 1776-03-09.
#    "publication_date": "1976-03-09",
#    "description": "A description of what builds nations' wealth.",
#    "creators": [{"name": "Smith, Adam",
#                  "affiliation": "University of Glasgow"}]
#    }}
#
## NOTE: Smith's ACCESS_TOKEN is not specified here. He would have to follow
## these steps: https://zenodo.org/dev#restapi-auth to obtain a value.
#d = Deposition(ACCESS_TOKEN, use_sandbox=True)
#d.append_file(book_path)
#d.metadata = book_metadata
#d.publish()
## Remove the PDF we downloaded
#os.remove(book_path)

if __name__ == '__main__':
    CLIENT_SECRETS_FILE = "client_secrets.txt"
    with open(CLIENT_SECRETS_FILE, 'r') as fid:
        ZENODO_TOKENS = [x for x in fid.read().split('\n') if x]
    
    use_sandbox = True
    
    conn = pymysql.connect(host='localhost', database='single_worm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    sql = '''
    SELECT *
    FROM experiments_valid
    WHERE exit_flag='END'
    '''
    
    cur.execute(sql)
    f_data = cur.fetchall()
    
    row = f_data[0]
    
    
    metadata = {'metadata':db_row2dict(row)}
    
    if use_sandbox:
        ZENODO_URL = "https://sandbox.zenodo.org/api/deposit/depositions"
        ACCESS_TOKEN = ZENODO_TOKENS[0]
    else:
        ZENODO_URL = "https://zenodo.org/api/deposit/depositions"
        ACCESS_TOKEN = ZENODO_TOKENS[1]
    
    r = requests.get(ZENODO_URL, params={'access_token': ACCESS_TOKEN})
    
    
    
#    ## NOTE: Smith's ACCESS_TOKEN is not specified here. He would have to follow
#    # these steps: https://zenodo.org/dev#restapi-auth to obtain a value.
#    dd = Deposition.list_all_depositions(zenodo_token, use_sandbox=use_sandbox)
#    print(dd)
#    

    
#    for rext in valid_ext:
#        upload_path = os.path.join(row['results_dir'], row['base_name'] + rext)
#        d.append_file(upload_path)
#    
#    d.publish()
    
    conn.close()    

#    
#    
#    ZENODO_SCOPE = "https://sandbox.zenodo.org/api/deposit/depositions"
#    
#    #https://zenodo.org/api/deposit/depositions?access_token=ZENODO_TOKEN
#    
#    
#    
#    
#    r = requests.get(ZENODO_SCOPE + ZENODO_TOKEN)
#    if r.status_code != 200:
#        print(r.json())
#
#
