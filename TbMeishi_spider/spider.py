#!/usr/bin/python
#coding=utf-8
#-------------------------------------------------------------------------------
# Name:        spider
# Purpose:     Selenium+Chrome/PhantomJS抓取淘宝美食
#
# Author:      
#
# Created:     2017年4月9日
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re
from pyquery import PyQuery as pq
from config import *
import pymongo
import json

# client = pymongo.MongoClient(MONGO_URL)
# db = client[MONGO_DB]

#Chrome
#browser = webdriver.Chrome()
#PhantomJS
#设置浏览器请求头
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = ( "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" )
browser = webdriver.PhantomJS(executable_path=r"r:\phantomjs-2.1.1-windows\bin\phantomjs.exe", desired_capabilities=dcap, service_args=SERVICE_ARGS)
browser.set_window_size(1400, 900)

print('游览器启动完成')
wait = WebDriverWait(browser, 10)

def wait_presence_of_element_located(selector):
    '''
    等待元素可见并返回
    :param selector: css选择器
    '''
    return wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )

def wait_element_to_be_clickable(selector):
    '''
    等待元素可见并可单击
    :param selector:
    '''
    return wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
    
def wait_text_to_be_present_in_element(selector, text_):
    '''
    检查文本是否在指定的元素里
    :param selector:
    :param text_:
    '''
    return wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), text_)
        )
    
    
def search():
    print('正在搜索')
    try:
        browser.get('https://www.taobao.com')
        input = wait_presence_of_element_located("#q")
        submit = wait_element_to_be_clickable("#J_TSearchForm > div.search-button > button")
        input.send_keys(KEYWORD)
        submit.click()
        total = wait_presence_of_element_located("#mainsrp-pager > div > div > div > div.total")
        get_products()
        return total.text
    except TimeoutException:
        return search()
    
def next_page(page_number):
    print('正在翻页', page_number)
    try:
        input = wait_presence_of_element_located("#mainsrp-pager > div > div > div > div.form > input")
        submit = wait_element_to_be_clickable("#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait_text_to_be_present_in_element('#mainsrp-pager > div > div > div > ul > li.item.active > span', str(page_number))
        get_products()
    except TimeoutException:
        return next_page(page_number)
    
def get_products():
    print('获得商品数据')
    wait_presence_of_element_located("#mainsrp-itemlist .items .item")
    html = browser.page_source
    doc = pq(html)
    items = doc("#mainsrp-itemlist .items .item").items()
    count = 0
    for item in items:
        product = {
            'image': 'https:' + str(item.find('.pic .J_ItemPic').attr('src')),
            'price': item.find('.price').text()[2:],
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
            }
        #print(product)
        write_to_file(product)
        #save_to_mongo(product)
        count = count + 1
    print('当前页商品数: ', count)

def save_to_mongo(result):
#     try:
#         if db[MONGO_TABLE].insert(result):
#             print('存储到MONGODB成功', result)
#     except Exception:
#         print('存储到MONGODB失败', result)
    pass

def write_to_file(content):
    with open('result.txt', 'a', encoding = 'utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
    pass

def main():
    try:
        total = search()
        total = int(re.compile('(\d+)').search(total).group(1))
        for i in range(2, total + 1):
            next_page( i)
    #except Exception as e:
    #    print('出错了', e)
    finally:
        #browser.close()
        browser.quit()
        pass

if __name__ == '__main__':
    main()
