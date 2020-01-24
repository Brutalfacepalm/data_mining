from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient


# 1) Написать программу, которая собирает входящие письма из своего или тестового
# почтового ящика и сложить данные о письмах в базу данных
# (от кого, дата отправки, тема письма, текст письма)

def run_database():
    client= MongoClient('localhost', 27017)
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
    letter_from = wdw.until(
        EC.presence_of_element_located((
            By.CLASS_NAME, 'letter__contact-item'
        ))
    )
    letter_date = wdw.until(
        EC.presence_of_element_located((
            By.CLASS_NAME, 'letter__date'
        ))
    )
    letter_title = wdw.until(
        EC.presence_of_element_located((
            By.CLASS_NAME, 'thread__subject_pony-mode'
        ))
    )
    # letter_body = driver.find_elements_by_xpath('//td[@class = "bodyContainer_mailru_css_attribute_postfix"]//td[@class="mcnTextContent_mailru_css_attribute_postfix"] | //div[@class="webkit_mailru_css_attribute_postfix"]/table/tbody//tr//tbody')
    # letter_body = '\n'.join(list(map(lambda x: x.text, letter_body)))
    letter_body = wdw.until(
        EC.presence_of_element_located((
            By.CLASS_NAME, 'letter-body__body-wrapper'
        ))
    )
    data = {'from':letter_from.text, 'date':letter_date.text, 'title':letter_title.text, 'text': letter_body.text}

    db['mail.ru'].update_one({'title': data['title']}, {'$set': data}, upsert=True)

    get_next_letter(driver.find_element_by_tag_name('html'))

    return driver


def stop_browser(driver):
    driver.quit()


def run_parse():
    LOGIN = 'study.ai_172@mail.ru'
    PASSWORD = 'NewPassword172'

    driver = run_browser()
    db = run_database()
    wdw = WebDriverWait(driver, 20)
    driver = login(driver, wdw, LOGIN, PASSWORD)
    driver = get_first_letter(driver, wdw)

    while True:
        driver = get_letter_data_and_next_page(driver, wdw, db)
    return driver


driver = run_parse()
