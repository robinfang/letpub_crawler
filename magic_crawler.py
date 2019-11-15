from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import pickle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import re
import pdb
import logging
import pandas as pd
import numpy as np

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def parseItem(i):
    try:
        first_td_list = i[0].find_elements_by_xpath('./td')
        first_record = map(lambda x: x.text, first_td_list)
        second_record = map(
            lambda x: x.find_elements_by_xpath('./td[2]')[0].text, i[1:])
    except:
        logging.exception("parse error")
    return list(first_record) + list(second_record)


class PageTurner(object):
    def __init__(self, driver, baseurl):
        self.driver = driver
        self.baseurl = baseurl
        self.currentPageNumber = 0

    def nextPage(self):
        self.currentPageNumber += 1
        nextPageUrl = self.baseurl.format(
            "currentpage={}".format(self.currentPageNumber))
        self.driver.get(nextPageUrl)


if __name__ == '__main__':

    # prox = Proxy()
    # prox.proxy_type = ProxyType.MANUAL
    # prox.http_proxy = "192.168.2.38:8848"
    # # prox.socks_proxy = "127.0.0.1:6666"
    # prox.ssl_proxy = "192.168.2.38:8848"

    capabilities = webdriver.DesiredCapabilities.CHROME
    # prox.add_to_capabilities(capabilities)

    driver = webdriver.Chrome(desired_capabilities=capabilities)
    url = "http://www.letpub.com.cn/index.php?page=grant&name=%E5%9C%B0%E7%90%86&person=&no=&company=&startTime=2015&endTime=2019&money1=&money2=&subcategory=&addcomment_s1=F&addcomment_s2=&addcomment_s3=&addcomment_s4=&{}#fundlisttable"
    pt = PageTurner(driver, url)
    pt.nextPage()
    time.sleep(5)
    lastpage_xpath = '//*[@id="main"]/table/tbody/tr[1]/td/a[last()]'
    lastpage_url = driver.find_elements_by_xpath(
        lastpage_xpath)[0].get_attribute("href")
    m = re.compile(".*currentpage=(\d+)").match(lastpage_url)
    lastpage = int(m.group(1))
    logging.info(lastpage)
    result = []
    while pt.currentPageNumber <= lastpage:

        item_list = driver.find_elements_by_xpath(
            '//*[@id="main"]/table/tbody/tr[position()>2 and position()<last()]')
        logging.info(len(item_list))
        length = int(len(item_list)/5)
        item_list = [item_list[i*5:5+5*i] for i in range(length)]
        result.extend(list(map(parseItem, item_list)))
        logging.info("current result list length:{}".format(len(result)))
        pt.nextPage()
    pd_df = pd.DataFrame(result)
    print(pd_df)
    pd_df.to_excel("letpub2.xlsx")
    driver.close()
