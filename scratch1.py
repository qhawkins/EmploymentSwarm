from selenium import webdriver
from time import sleep

driver = webdriver.Chrome()
driver.get('https://www.google.com')
sleep(1)
screenshot = driver.get_screenshot_as_base64()

print(screenshot)