import time
import os
import pymysql
import shutil
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#%%
tmp_dir = '/Users/ajaver/Tmp'
use_sandbox = False
#%%
CLIENT_SECRETS_FILE = "client_secrets.txt"
with open(CLIENT_SECRETS_FILE, 'r') as fid:
    ZENODO_TOKENS = [x for x in fid.read().split('\n') if x]
    if use_sandbox:
        ZENODO_URL = "https://sandbox.zenodo.org/"
        ACCESS_TOKEN = ZENODO_TOKENS[0]
    else:
        ZENODO_URL = "https://zenodo.org/"
        ACCESS_TOKEN = ZENODO_TOKENS[1]
zenodo_api_url = ZENODO_URL + 'api/deposit/depositions/'

#%%
conn = pymysql.connect(host='localhost', database='single_worm_db')
cur = conn.cursor(pymysql.cursors.DictCursor)

sql = '''
SELECT z.experiment_id, z.zenodo_id, z.filename, ev.base_name, ev.results_dir
FROM zenodo_files AS z
JOIN experiments_valid AS ev ON ev.experiment_id = z.experiment_id
WHERE file_type_id = 2
AND z.experiment_id NOT IN (SELECT z1.experiment_id FROM zenodo_files AS z1 WHERE z1.file_type_id = 1)
'''
cur.execute(sql)
zenodo_files = cur.fetchall()
#%%
e_path = os.path.join(os.environ['HOME'], 'Github/single-worm-analysis/upload_zenodo/geckodriver')
browser = webdriver.Firefox(executable_path = e_path)

browser.get(ZENODO_URL + 'oauth/login/github/')


username = browser.find_element_by_id("login_field")
password = browser.find_element_by_id("password")
username.send_keys("ver228@gmail.com")

input("Press Enter to continue...")

len(zenodo_files)
#%%
for irow, row in enumerate(zenodo_files):
    print(irow+1, len(zenodo_files))
    
    old_name = os.path.join(row['results_dir'], row['base_name'] + '.hdf5')
    new_name = os.path.join(tmp_dir, row['filename'].replace('_features.hdf5', '.hdf5'))
    shutil.copyfile(old_name, new_name)
    #%%
    deposition_url = '{}deposit/{}'.format(ZENODO_URL, row['zenodo_id'])
    browser.get(deposition_url)
    #%%
    elm = browser.find_element_by_xpath("//input[@type='file']")
    elm.send_keys(new_name)
    
    upload_button = browser.find_element_by_xpath("//button[contains(.,'Start upload')]")
    while not upload_button.is_enabled():
        time.sleep(1)
    upload_button.click()
    #%%
    url_f = '{}{}/files'.format(zenodo_api_url, row['zenodo_id'])
    #%%
    print(new_name, 'Uploading file...')
    while True:
        time.sleep(3)
        r = requests.get(url_f, params={'access_token': ACCESS_TOKEN})
        q = [x for x in r.json() if x['filename'] == os.path.basename(new_name)]
        if len(q)>0:
            assert len(q) == 1
            q = q[0]
            break 
    save_button = browser.find_element_by_xpath("//button[contains(.,'Save')]")  
    save_button.click()
    
    sql = '''
    INSERT INTO zenodo_files (experiment_id, file_id, zenodo_id, filename, filesize, checksum, file_type_id) 
    VALUES({}, "{}", {}, "{}", {}, "{}", {});
    '''.format(row['experiment_id'], q['id'] , row['zenodo_id'], q['filename'], q['filesize'], q['checksum'], 1)
    cur.execute(sql)
    conn.commit()
    
    #cleaning
    os.remove(new_name)

browser.close()


