from selenium import webdriver
from  selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get('https://geekbrains.ru/login')

assert "GeekBrains" in driver.title

elem = driver.find_element_by_id('user_email')
elem.send_keys('theshick@mail.ru')
elem = driver.find_element_by_id('user_password')
elem.send_keys('499495Facepalm')

elem.send_keys(Keys.RETURN)
assert "Главная" in driver.title

profile = driver.find_element_by_class_name('avatar')
driver.get(profile.get_attribute('href'))

edit_profile = driver.find_element_by_class_name('text-sm')
driver.get(edit_profile.get_attribute('href'))





# driver.quit()