#!/usr/bin/python
#coding=utf-8
#-------------------------------------------------------------------------------
# Name:        spider
# Purpose:     分析Ajax抓取今日头条街拍美图
#
# Author:
#
# Created:     31-03-2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode
import json
from bs4 import BeautifulSoup
import re
from config import *
from hashlib import md5
#import pymongo
from multiprocessing import Pool
#from json import JSONDecodeError

#client = pymongo.MongoClient(MONGO_URL, connect=False)
#db = client[MONGO_DB]

def get_page_index(offset, keyword):
    data = {
        'offset':offset,
        'format':'json',
        'keyword':keyword,
        'autoload':'true',
        'count':20,
        'cur_tab':3
    }
    url = 'http://www.toutiao.com/search_content/?' + urlencode(data)
    print('([%d] 正在下载索引页 %s' % (os.getpid(), url))
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出错', url)
        return None

def parse_page_index(html):
    #try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    #except JSONDecodeError:
    #    pass

def get_page_detail(url):
    print('([%d] 正在下载详细页 %s' % (os.getpid(), url))
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错', url)
        return None

def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'html5lib')
    title = soup.select('title')[0].get_text()
    print(title)
    images_pattern = re.compile('var gallery = (.*?);', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images: download_img(image)
            return {
                'title': title,
                'url': url,
                'images': images
            }

def save_to_mongo(result):
##    if db[MONGO_TABLE].insert(result):
##        print('存储到MongoDB成功', result)
##        return True
    return False

def download_img(url):
    print('([%d] 正在下载图片 %s' % (os.getpid(), url))
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image( response.content)
        return None
    except RequestException:
        print('请求图片出错', url)
        return None

def save_image(content):
    file_path = '{0}/images/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    print('获取索引页 (%d)' % offset)
    html = get_page_index(offset, KEYWORD)
    for url in parse_page_index(html):
        html = get_page_detail( url)
        if html:
            result = parse_page_detail(html, url)
            if result: save_to_mongo( result)
    pass

if __name__ == '__main__':
    groups = [x*20 for x in range(GROUP_START, GROUP_END)]
    pool = Pool(processes=PROCESSE_NUM)
    pool.map(main, groups)