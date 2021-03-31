from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import datetime
import time
import os


#variables
location = "방이동"
search_bar = "*[id^='input_search1']" # issue 1 : id값의 변동으로 1이 아닌 다른 숫자가 올 가능성이 존재.

#set up driver

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.headless = True
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15")
options.add_argument("lang=ko_KR")


try:
    driver = webdriver.Chrome("/Users/ME/Desktop/Works/Major/Business/Capston Project/Project/chromedriver")
    driver.implicitly_wait(3)

    #run page
    driver.get("https://map.naver.com/v5/")

    driver.find_element_by_css_selector(search_bar).send_keys(location + " 음식점")
    driver.find_element_by_css_selector(search_bar).send_keys(Keys.ENTER)

    #음식점 스크롤 내리기

    def doScrollDown(whileSeconds):
        start = datetime.datetime.now()
        end = start + datetime.timedelta(seconds=whileSeconds)
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(1)
            if datetime.datetime.now() > end:
                break

    doScrollDown(4)

    #음식점 클릭
    for button in driver.find_elements_by_xpath('//*[@id="_pcmap_list_scroll_container"]/ul'):
        button.click()
        #변경된 url html 추출
        response_url = requests.get(driver.current_url)
        try:
            page = urlopen(response_url)
        except:
            print("Error in urlopen.")

        soup = BeautifulSoup(page,"html.parser")

        #음식점 세부 페이지에서 [지역-구/동][음식점이름][음식카테고리][주소][음식이름] [음식사진] ['음식태그'사진]* [음식태그사진한줄평] 가져오기

    #다음페이지 클릭
    driver.find_element_by_xpath('//*[@id="app-root"]').click()

finally:
    driver.close()
