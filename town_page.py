
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import csv
import requests
import time
import re
import asyncio


def setUpWebzDriver(url: str, waitSec: int):
    # オプションを記述し勝手にブラウザが閉じるのを防ぐ
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    # 　ブラウザを表示しない
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(
        ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(waitSec)
    return driver


async def searchKeywordAndArea(driver: webdriver, keyword: str, area: str):
    searchWordInputBox = await driver.find_element(
        By.ID, "keyword-suggest").find_element(By.CLASS_NAME, "a-text-input")
    searchWordInputBox.send_keys(keyword)
    areaInputBox = await driver.find_element(
        By.ID, "area-suggest").find_element(By.CLASS_NAME, "a-text-input")
    areaInputBox.send_keys(area)
    submitButton = await driver.find_element(By.CLASS_NAME, "m-keyword-form__button")
    submitButton.click()


async def fetchTitles(soup: BeautifulSoup):
    titles = []
    title_links = soup.find_all(
        'a', attrs={"class": "m-article-card__header__title__link"})
    for title in title_links:
        titles.append(title.text.strip())
    return titles


async def fetchPhoneNumbers(soup: BeautifulSoup):
    numbers = []
    phone_numbers = soup.find_all(
        'p', attrs={"class": "m-article-card__lead__caption"})
    for phone in phone_numbers:
        if (phone.text.split('【')[1].split('】')[0] == "電話番号"):
            numbers.append(phone.text.split('】')[1].strip())
    return numbers


async def fetchAddresses(soup: BeautifulSoup):
    numbers = []
    addresses = soup.find_all(
        'p', attrs={"class": "m-article-card__lead__caption"})
    for address in addresses:
        if (address.text.split('【')[1].split('】')[0] == "住所"):
            numbers.append(address.text.split('】')[1].strip())
    return numbers


async def main():

    ##################
    keyword = "旅館"
    area = "兵庫県豊岡市"
    dataSize = 50  # dataSize * 20 === 50 * 20 => 1000
    ###################

    url = "https://itp.ne.jp"
    driver = setUpWebzDriver(url, 1)
    searchWordInputBox = driver.find_element(
        By.ID, "keyword-suggest").find_element(By.CLASS_NAME, "a-text-input")
    searchWordInputBox.send_keys(keyword)
    areaInputBox = driver.find_element(
        By.ID, "area-suggest").find_element(By.CLASS_NAME, "a-text-input")
    areaInputBox.send_keys(area)
    submitButton = driver.find_element(By.CLASS_NAME, "m-keyword-form__button")
    submitButton.click()
    try:
        index = 0
        # 一回で20件取得 20 * 50 = 1000件
        while driver.find_element(By.CLASS_NAME, 'm-read-more') or index < dataSize:
            button = driver.find_element(By.CLASS_NAME, 'm-read-more')
            button.click()
            time.sleep(1)
            index += 1

    except NoSuchElementException:
        pass
    time.sleep(dataSize + 3)
    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')
    titles = await fetchTitles(soup)
    numbers = await fetchPhoneNumbers(soup)
    addersses = await fetchAddresses(soup)
    df = pd.DataFrame({
        "会社名": titles,
        "電話番号": numbers,
        "住所": addersses
    })
    df.to_csv(f'{keyword}_{area}_{len(titles)}件.csv', index=False)


asyncio.run(main())
