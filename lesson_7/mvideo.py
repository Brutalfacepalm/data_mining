from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import time
from selenium.webdriver.common.action_chains import ActionChains


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
    hits_block = wdw.until(
        EC.presence_of_element_located((
            By.CLASS_NAME, 'sel-hits-block'
        ))
    )
    actions = ActionChains(driver)
    actions.move_to_element(hits_block)
    actions.perform()
    return hits_block


def get_next_hits_block(wdw_hits):
    try:
        hits_block = wdw_hits.until(
            EC.presence_of_element_located((
                By.XPATH, '//a[contains(@class, "sel-hits-button-next disabled")]'
            ))
        )
        return None
    except:
        hits_block = wdw_hits.until(
            EC.presence_of_element_located((
                By.CLASS_NAME, 'sel-hits-button-next'
            ))
        )
    return wdw_hits


def get_hits_data_and_next_block(driver, wdw_hits, db):
    while True:
        next_block = get_next_hits_block(wdw_hits)
        if next_block:
            hits_info = wdw_hits.until(
                EC.presence_of_element_located((
                    By.XPATH, '//a[contains(@class, "sel-product-tile-title")/@data-product-info]'
                ))
            )


            next_block.click()
        else:
            hits_info = None
            break
    return hits_info

def stop_browser(driver):
    driver.quit()


def run_parse():
    driver = run_browser()

    db = run_database()
    wdw = WebDriverWait(driver, 10)
    wdw_hits = get_hits_block_as_driver(driver, wdw)
    wdw_hits = WebDriverWait(wdw_hits, 10)


    while True:
        hits_info = get_hits_data_and_next_block(driver, wdw_hits, db)
        print(hits_info)
        if hits_info == None:
            break
    return hits_info


driver = run_parse()
