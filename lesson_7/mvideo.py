from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import time
from selenium.webdriver.common.action_chains import ActionChains
import json


def run_database():
    client = MongoClient('localhost', 27017)
    db = client.mvideo_base
    return db


def run_browser():
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.mvideo.ru/')
    return driver


def get_hits_block_as_driver(driver, wdw):
    hits_block = wdw.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'sel-hits-block')))[0]
    actions = ActionChains(driver)
    actions.move_to_element(hits_block)
    actions.perform()
    return hits_block


def get_next_hits_block(wdw_hits):
    try:
        hits_block = wdw_hits.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "sel-hits-button-next disabled")]')))
        return None
    except:
        hits_block = wdw_hits.until(EC.presence_of_element_located((By.CLASS_NAME, 'sel-hits-button-next')))
    return hits_block


def get_hits_data_and_next_block(wdw_hits, db):
    block_info = wdw_hits.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-init="gtm-push-products"]')))
    for block in block_info:
        name_block = block.find_element_by_class_name('gallery-title-wrapper').text
        if 'Хиты продаж' in name_block:
            block = WebDriverWait(block, 10)
            hits_info = block.until(EC.visibility_of_any_elements_located((By.CLASS_NAME, 'sel-product-tile-title')))
            for hit in hits_info:
                hit = hit.get_attribute("data-product-info")
                hit = json.loads(hit)
                name = hit['productName']
                price = hit['productPriceLocal']
                category = hit['productCategoryName']
                vendor = hit['productVendorName']
                hit = {'name': name, 'price': price, 'category': category, 'vendor': vendor}
                update_db(hit, db)

    next_block = get_next_hits_block(wdw_hits)
    if next_block:
        next_block.click()
        time.sleep(1)
    else:
        hits_info = None
    return hits_info


def update_db(hits_info, db):
    db['mvideo.ru'].update_one({'name': hits_info['name']}, {'$set': hits_info}, upsert=True)


def stop_browser(driver):
    driver.quit()


def run_parse():
    driver = run_browser()
    db = run_database()
    wdw = WebDriverWait(driver, 10)
    wdw_hits = get_hits_block_as_driver(driver, wdw)
    wdw_hits = WebDriverWait(wdw_hits, 10)

    while True:
        hits_info = get_hits_data_and_next_block(wdw_hits, db)
        if hits_info == None:
            break
    return hits_info


driver = run_parse()