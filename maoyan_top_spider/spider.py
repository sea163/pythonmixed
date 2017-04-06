#!/usr/bin/python
#coding=utf-8
#-------------------------------------------------------------------------------
# Name:        spider
# Purpose:     Requests+正则表达式抓取猫眼电影TOP100
#
# Author:
#
# Created:     06-04-2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import requests
from requests.exceptions import RequestException
import re
import json
from multiprocessing import Pool

def get_one_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None
    pass

def parse_one_page(html):
    pattern = re.compile('<dd>.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
        + '.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
        + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }
    pass

def write_to_file(content):
    with open('result.txt', 'a', encoding = 'utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
    pass

def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)
    pass

if __name__ == '__main__':
    pool = Pool(processes=2)
    pool.map(main, [i*10 for i in range(10)])