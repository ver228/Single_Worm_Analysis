import time
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


browser = webdriver.Firefox(executable_path = '/Users/ajaver/Documents/GitHub/single-worm-analysis/upload_zenodo/geckodriver 3')
browser.get('https://sandbox.zenodo.org/oauth/login/github/')


username = browser.find_element_by_id("login_field")
password = browser.find_element_by_id("password")



browser.find_elements_by_name("commit")[0].click()

#%%
browser.implicitly_wait(5)
deposition_url = 'https://sandbox.zenodo.org/deposit/101873'

browser.get(deposition_url)

dd = '/Users/ajaver/Documents/GitHub/tierpsy-tracker/tests/data/WT2/MaskedVideos/WT2.hdf5'
elm = browser.find_element_by_xpath("//input[@type='file']")
elm.send_keys(dd)

upload_button = browser.find_element_by_xpath("//button[contains(.,'Start upload')]")

while not upload_button.is_enabled():
    time.sleep(1)
upload_button.click()

    