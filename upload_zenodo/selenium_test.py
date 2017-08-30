from selenium import webdriver
from selenium.webdriver.common.keys import Keys

browser = webdriver.Firefox()
browser.get('https://sandbox.zenodo.org/deposit/101809')

upload_button = browser.find_element_by_xpath("//button[contains(.,'Choose files')]")
upload_button.click()


dd = '/Users/ajaver/Documents/GitHub/tierpsy-tracker/tests/data/WT2/MaskedVideos/WT2.hdf5'