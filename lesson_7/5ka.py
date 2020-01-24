from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

options = Options()
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)
driver.get('https://5ka.ru/special_offers')
print('Открыта главная страница')
while True:
    try:
        more_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CLASS_NAME, 'special-offers__more-btn'
            ))
        )
        more_btn.click()
    except Exception as e:
        print(e)
        break
goods = driver.find_elements_by_class_name('sale-card')
for good in goods:
    print(good.find_element_by_class_name('sale-card__title').text)
    print(float(good
                .find_element_by_class_name('sale-card__price--new')
                .find_element_by_xpath('span[1]')
                .text)/100
          )