from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import time


def run_database():
    client = MongoClient('localhost', 27017)
    db = client.mail_base
    return db


def run_browser():
    options = Options()
    options.add_argument('--start-maximized')

    driver = webdriver.Chrome(options=options)
    driver.get('https://mail.ru/')
    return driver


def login(driver, wdw, LOGIN, PASSWORD):
    login = driver.find_element_by_id('mailbox:login')
    login.send_keys(LOGIN)
    login.send_keys(Keys.RETURN)

    password = wdw.until(
        EC.visibility_of_element_located((
            By.CLASS_NAME, 'mailbox__input_password'
        ))
    )
    password.send_keys(PASSWORD)
    password.send_keys(Keys.RETURN)
    return driver


def get_first_letter(driver, wdw):
    first_letter = wdw.until(
        EC.presence_of_all_elements_located((
            By.CLASS_NAME, 'js-letter-list-item'
        ))
    )[0]
    first_letter.click()

    return driver


def get_next_letter(letter):
    try:
        letter.send_keys(Keys.CONTROL, Keys.ARROW_DOWN)
    except Exception as e:
        print(e)


def get_letter_data_and_next_page(driver, wdw, db):
    time.sleep(1)
    letter_from = wdw.until(
        EC.presence_of_element_located((
            By.CLASS_NAME, 'letter__contact-item'
        ))
    ).text
    letter_date = wdw.until(
        EC.presence_of_element_located((
            By.CLASS_NAME, 'letter__date'
        ))
    ).text
    letter_title = wdw.until(
        EC.presence_of_element_located((
            By.CLASS_NAME, 'thread__subject_pony-mode'
        ))
    ).text

    letter_body = wdw.until(
        EC.presence_of_element_located((
            By.CLASS_NAME, 'letter-body'
        ))
    ).text
    data = {'from': letter_from, 'date': letter_date, 'title': letter_title, 'text': letter_body}

    db['mail.ru'].update_one({'title': data['title']}, {'$set': data}, upsert=True)

    try:
        driver.find_element_by_class_name('portal-menu-element_next').find_element_by_class_name('button2_disabled')
        return None
    except:
        pass

    get_next_letter(driver.find_element_by_tag_name('html'))

    return driver


def stop_browser(driver):
    driver.quit()


def run_parse():
    LOGIN = 'study.ai_172@mail.ru'
    PASSWORD = 'NewPassword172'

    driver = run_browser()
    db = run_database()
    wdw = WebDriverWait(driver, 10)
    driver = login(driver, wdw, LOGIN, PASSWORD)
    driver = get_first_letter(driver, wdw)

    while True:
        driver = get_letter_data_and_next_page(driver, wdw, db)
        if driver == None:
            break
    return driver


driver = run_parse()
