from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.keys import Keys
import requests
from multiprocessing import Pool
import multiprocessing
from urllib.request import urlopen, Request
from urllib.parse import quote_plus
import json

class page:
    def __init__(self, driverDir):

        options = Options()
        options.add_argument("disable-infobars")
        options.add_argument("enable-automation")
        options.add_argument('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome')
        self.driver = webdriver.Chrome(driverDir, options = options)
        
    def open(self, url):
        
        self.driver.get(url)
        time.sleep(5)
    
    def login(self, userId, userPw):
        
        idField = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
        pwField = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
        idField.clear()
        pwField.clear()
        idField.send_keys(userId)
        pwField.send_keys(userPw)
        time.sleep(11)
        
        loginButton = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]')
        loginButton.click()
        time.sleep(11)
        
        noSaveButton = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button')
        noSaveButton.click()
        time.sleep(15)
        
        noAlarmButton = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div[3]/button[2]")
        noAlarmButton.click()
        time.sleep(11)
        
    def search(self, tag):
        
        tagUrl = "https://www.instagram.com/explore/tags/" + tag
        self.driver.get(tagUrl)
        time.sleep(11)
        
    def openFirst(self):
        firstPost = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a')
        firstPost.click()
        time.sleep(10)
        
    def getDriver(self):
        return (self.driver)

class list_page:
    
    def __init__(self, driver):
        self.driver = driver
        self.url_list = []

    def crawling(self, page_num):
        body = self.driver.find_element_by_tag_name("body")
        for i in range(page_num):
            print("scroll: ", i)
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(5)
            
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            urls = soup.select("article.KC1QD div.Nnq7C div.v1Nh3 a")
            for u in urls:
                self.url_list.append(u["href"])
    
    def get_driver(self):
        return self.driver
    
    def get_url_list(self):
        return list(set(self.url_list))