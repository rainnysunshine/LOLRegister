import argparse
import re
import time
from random import random
from time import sleep

import requests
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from PIL import Image
import base64

from Config import Config
from constants import CAPTCHA_RESIZED_IMAGE_FILE_PATH, CAPTCHA_SINGLE_IMAGE_FILE_PATH
from src.CaptchaResolver import CaptchaResolver

webOption = webdriver.ChromeOptions()
webOption.add_experimental_option("detach", True)
webOption.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36')

driver = webdriver.Chrome(options=webOption)
driver.implicitly_wait(7)

logger.add("./config/app.log", rotation="500MB", compression='zip')

with open('./config/stealth.min.js') as f:
    js = f.read()
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": js
})


def sendKeys(selector: WebElement, message: str):
    selector.send_keys(message)


def WebElementExist(type: str, string: str):
    elements = []
    if type == 'xpath':
        elements = driver.find_elements(By.XPATH, string)
    if type == 'css':
        elements = driver.find_elements(By.CSS_SELECTOR, string)
    if type == 'classname':
        elements = driver.find_elements(By.CLASS_NAME,string)
    if len(elements) == 0:
        return None
    else:
        return elements[0]


# 获取captcha所在的iframe
def get_captcha_content_iframe() -> WebElement:
    driver.switch_to.default_content()
    captcha_content_iframe: WebElement
    element = WebElementExist('xpath', '//iframe[contains(@title, "hCaptcha挑戰")]')
    if element:
        captcha_content_iframe = element
    # if WebElementExist('')

    # captcha_content_iframe = driver.find_element(By.XPATH, '//iframe[contains(@title, "hCaptcha挑戰")]' )
    return captcha_content_iframe


# 切换driver到captcha所在的iframe
def switch_to_captcha_content_iframe() -> None:
    captcha_content_iframe: WebElement = get_captcha_content_iframe()
    driver.switch_to.frame(captcha_content_iframe)


# 获取验证提问的文字
def get_captcha_target_text():
    captcha_target_name_element: WebElement = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'prompt-text')))
    return captcha_target_name_element.text


# 获取验证图片并提交验证，最后点击验证
def verify_captcha():
    # 获取问题文字
    captcha_target_text = get_captcha_target_text()
    logger.debug(f'captcha_target_text {captcha_target_text}')
    single_captcha_elements = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(
        (By.CSS_SELECTOR, '.task-image .image-wrapper .image')))
    resized_single_captcha_base64_strings = []
    for i, single_captcha_element in enumerate(single_captcha_elements):
        single_captcha_element_style = single_captcha_element.get_attribute('style')
        pattern = re.compile('url\("https.*?"\)')
        match_result = re.search(pattern, single_captcha_element_style)
        single_captcha_element_url = match_result.group() if match_result else None
        single_captcha_element_url = single_captcha_element_url[5:-2]
        logger.debug(f'single_captcha_element_url {single_captcha_element_url}')

        with open(CAPTCHA_SINGLE_IMAGE_FILE_PATH % (i,), 'wb') as f:
            f.write(requests.get(single_captcha_element_url).content)
        resized_single_captcha_base64_string = resize_base64_image(
            CAPTCHA_SINGLE_IMAGE_FILE_PATH % (i,), (100, 100), i)
        resized_single_captcha_base64_strings.append(resized_single_captcha_base64_string)

    logger.debug(
        f'length of single_captcha_element_urls {len(resized_single_captcha_base64_strings)}'
    )

    captcha_resolver = CaptchaResolver()
    captcha_recognize_result = captcha_resolver.create_task(
        question=captcha_target_text,
        queries=resized_single_captcha_base64_strings
    )
    if not captcha_recognize_result:
        logger.error('could not get captcha recognize result')
        return
    recognized_results = captcha_recognize_result.get(
        'solution', {}).get('objects')
    if not recognized_results:
        logger.error('count not get captcha recognized indices')
        return

    recognized_indices = [i for i, x in enumerate(recognized_results) if x]
    logger.debug(f'recognized_indices {recognized_indices}')
    click_targets = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(
        (By.CSS_SELECTOR, '.task-image')
    ))
    for recognized_index in recognized_indices:
        click_target: WebElement = click_targets[recognized_index]
        click_target.click()
        time.sleep(random())

    submit: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.button-submit')))
    submit.click()


# 调整图片大小，并将其转换成base64编码字符串返回
def resize_base64_image(filename, size, num) -> str:
    width, height = size
    img = Image.open(filename)
    new_img = img.resize((width, height))
    new_img.save(CAPTCHA_RESIZED_IMAGE_FILE_PATH % (num,))
    with open(CAPTCHA_RESIZED_IMAGE_FILE_PATH % (num,), 'rb') as f:
        data = f.read()
        encoded_string = base64.b64encode(data)
        return encoded_string.decode('utf-8')


def init() -> Config:
    parser = argparse.ArgumentParser(description='可以命令行指定配置文件位置')
    parser.add_argument('-c', '--config', dest="configPath", default="./settings/config.yaml")
    args = parser.parse_args()

    config = Config(args.configPath)
    return config


def main(email: str, account: dict, index: int):
    js = 'window.open("https://signup.br.leagueoflegends.com/zh-tw/signup/index#/");'
    driver.execute_script(js)
    # driver.close()
    driver.switch_to.window(driver.window_handles[index + 1])
    '//*[@id="root"]/div/div/div[2]/div[1]/form/div[1]/input'
    inputEmail = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/form/div[1]/input')
    inputEmail.send_keys(email)
    driver.find_element(By.XPATH, '//*[@class="next-button"]/button').click()

    day = Select(driver.find_element(By.NAME, 'dob-day'))
    day.select_by_value("1")
    month = Select(driver.find_element(By.NAME, 'dob-month'))
    month.select_by_value("1")
    year = Select(driver.find_element(By.NAME, 'dob-year'))
    year.select_by_value("2000")

    driver.find_element(By.XPATH, '//*[@class="next-button"]/button').click()
    sleep(1)
    usernameSelector = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/form/div[1]/input')))
    usernameSelector.send_keys(account["username"])

    passwordSelector = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/form/div[2]/input')
    password = account["password"]
    sendKeys(passwordSelector, password)

    confirmpasswordSelector = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/form/div[3]/input')
    sendKeys(confirmpasswordSelector, password)

    tables = driver.find_elements(By.CLASS_NAME, 'control-checkbox')
    for table in tables:
        table.send_keys(Keys.SPACE)

    driver.find_element(By.XPATH, '//*[@class="next-button"]/button').click()

    switch_to_captcha_content_iframe()
    verify_captcha()
    sleep(5)
    # 判断是否会出现”进行顺利吗？“页面，如果出现，需要重新点击确认
    # WebDriverWait(driver, 5).until(driver.switch_to.default_content())

    driver.switch_to.default_content()
    element_exist = WebElementExist('css', '.scene-heading')
    if element_exist:
        title_now = element_exist.text
        if title_now == '進行順利嗎？':
            driver.find_element(By.CSS_SELECTOR, '.next-button').click()
            switch_to_captcha_content_iframe()
            verify_captcha()


if __name__ == '__main__':
    config = init()
    accounts = config.accounts
    email = config.email


    for i, account in enumerate(accounts):
        main(email, accounts[account], i)
