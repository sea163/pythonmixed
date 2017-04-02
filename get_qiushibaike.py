#!/usr/bin/python
#coding=utf-8
#-------------------------------------------------------------------------------
# Name:        糗事百科-热门下载
# Purpose:     根据 http://cuiqingcai.com/990.html 代码修改
#              从糗事百科下载8小时热门的全部内容格式化保存到txt方便用静读天下朗读
# Author:      sea
#
# Created:     28-01-2017
# Copyright:   (c) sea 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys
if sys.version_info[0] == 3:
    import urllib.request
    import urllib.error
    import http.client
else:
    reload(sys)
    sys.setdefaultencoding('utf-8')
    import urllib2
import os
import re
import codecs
import time
import random
from datetime import datetime

#封装字典,访问字典元素支持属性方式访问
class Storage(dict):
    def __init__(self, *args, **kw):
        super(Storage, self).__init__(self, *args, **kw)

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

class QSBK_Download:
    #正则表达式相关
    #文档块正则 获得完整的文档块
    RE_ARTICLE_BLOCK = r'class="article block.+?>.+?(?:</div>\s</a>\s+?</div>|single-clear"></div>\s+?</div>)'
    #文档作者
    RE_AUTHOR = r'<h2>(.*?)<'
    #文档详细URL
    RE_CONTENT_HERF = r'<a href="(/article/\d+)'
    #文档内容
    RE_CONTENT = r'<div class="content">(.*?)</div'
    #文档内容包含图片
    RE_CONTENT_IMG = r'<div class="thumb">(.*?)</div'
    #好笑
    RE_STATS_VOTE_NUM = r'class="stats-vote"><i class="number">(\d+)'
    #评论数
    RE_STATS_COMMENTS_NUM = r'(\d+)</i> 评论'
    #神评作者
    RE_CMT_NAME = r'cmt-name">(.+?)[：\.<]'
    #神评内容
    RE_MAIN_TEXT = r'main-text">\s：(.+?)<'
    #基本URL
    BASE_URL = 'http://www.qiushibaike.com'
    #首页
    MAIN_URL = 'http://www.qiushibaike.com/8hr/page/1'
    #游览器模拟
    USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    #每读取一页网页后延迟时间 最小,最大 (秒)
    DELAY_INTERVAL = (2,4)

    def __init__(self):
        #初始化headers
        self.headers = { 'User-Agent' : QSBK_Download.USER_AGENT }
        #存放段子的变量，每一个元素存放一个段子
        self.stories = []
        #下一页段子的链接
        self.nexturl = None
        #当前段子内容
        self.storyText = ''
        #编译正则表达式
        #文档块正则 获得完整的文档块
        self.pattern_article_block = re.compile(QSBK_Download.RE_ARTICLE_BLOCK,re.S)
        #文档作者
        self.pattern_author = re.compile(QSBK_Download.RE_AUTHOR,re.S)
        #文档详细URL
        self.pattern_content_herf = re.compile(QSBK_Download.RE_CONTENT_HERF,re.S)
        #文档内容
        self.pattern_content = re.compile(QSBK_Download.RE_CONTENT,re.S)
        #文档内容包含图片
        self.pattern_content_img = re.compile(QSBK_Download.RE_CONTENT_IMG,re.S)
        #好笑
        self.pattern_stats_vote_num = re.compile(QSBK_Download.RE_STATS_VOTE_NUM,re.S)
        #评论数
        self.pattern_comments_num = re.compile(QSBK_Download.RE_STATS_COMMENTS_NUM,re.S)
        #神评作者
        self.pattern_cmt_name = re.compile(QSBK_Download.RE_CMT_NAME,re.S)
        #神评内容
        self.pattern_cmt_text = re.compile(QSBK_Download.RE_MAIN_TEXT,re.S)

        pass

    def getPage(self, url):
        #获得一个内容页面
        if sys.version_info[0] == 3:
            #python 3
            try:
                #构建请求的request
                request = urllib.request.Request(url, headers = self.headers)
                #利用urlopen获取页面代码
                response = urllib.request.urlopen( request)
                #byte to utf-8
                pageCode = response.read().decode('utf-8')
                return pageCode
            except urllib.error.URLError as e:
                if hasattr(e,"reason"):
                    print("连接糗事百科失败,错误原因", e.reason)
                return None
            except http.client.BadStatusLine as e:
                if hasattr(e,"reason"):
                    print("连接糗事百科失败,错误原因", e.reason)
                return None
        else:
            #python 2
            try:
                #构建请求的request
                request = urllib2.Request(url, headers = self.headers)
                #利用urlopen获取页面代码
                response = urllib2.urlopen( request)
                #byte to utf-8
                pageCode = response.read().decode('utf-8')
                return pageCode
            except urllib2.URLError as e:
                if hasattr(e,"reason"):
                    print("连接糗事百科失败,错误原因", e.reason)
                return None

    def html2text(self, html):
        #html 标签过滤
        html = html.replace('<span>', '')
        html = html.replace('</span>', '')
        html = html.replace('<br/>', '\n')
        #html = html2text.html2text(html)
        return html

    def getStoryField(self, pattern, default='None'):
        #获得段子中的字段
        m = re.search(pattern, self.storyText)
        if m:
            return m.group(1)
        else:
            return default


    def getPageItems(self,url):
        #获得一个内容页面中的段子
        pageCode = self.getPage(url)
        if not pageCode:
            print("页面加载失败....")
            return None

        #检查是否有下一页并获得链接
        istart = pageCode.find('下一页')
        #print("istart1 %d" % istart)
        if istart != -1:
            #存在下一页
            #获得下一页标签开始位置
            istart = pageCode.rfind('<li>', 0, istart)
            #通过正则获取下一页url
            pattern = re.compile('href="(.*?)"')
            m = pattern.search(pageCode, istart)
            if m:
                self.nexturl = QSBK_Download.BASE_URL + m.group(1)
                #print(self.nexturl)

        items = re.findall( self.pattern_article_block, pageCode)
        print( "页 %s 获得段子 %d 个" % (url, len(items)))
        #从每个段子获得关键字段并存入stories
        for item in items:
            #保存当前段子内容
            self.storyText = item;
            #print(item)
            #忽略包含图片的内容
            m = re.search(self.pattern_content_img, self.storyText)
            if m:
                print("忽略包含图片的段子...")
                continue
            #字典
            story = Storage()
            #文档作者
            story.author = self.getStoryField(self.pattern_author).strip()
            #文档详细URL
            story.content_herf = QSBK_Download.BASE_URL + self.getStoryField(self.pattern_content_herf)
            #文档内容
            story.content = self.html2text( self.getStoryField(self.pattern_content).strip())
            #好笑
            story.stats_vote_num = self.getStoryField(self.pattern_stats_vote_num, '0')
            #评论数
            story.comments_num = self.getStoryField(self.pattern_comments_num, '0')
            #神评作者
            story.cmt_name = self.getStoryField(self.pattern_cmt_name).strip()
            #神评内容
            story.cmt_text = self.getStoryField(self.pattern_cmt_text).strip()
            #print( story)
            #加入存储列表
            self.stories.append( story)
        return len(items)

    def getAll(self):
        #获得8小时内热门段子
        #初始化下一个段子的链接
        self.nexturl = QSBK_Download.MAIN_URL
        while self.nexturl:
            url = self.nexturl
            #清空下一个页url标记
            self.nexturl = None
            self.getPageItems( url)
            #break
            #等待一下避免被防火墙拦截
            time.sleep( random.randint(QSBK_Download.DELAY_INTERVAL[0], QSBK_Download.DELAY_INTERVAL[1]))
        pass

    def save(self):
        #保存段子到文件
        if len(self.stories) == 0:
            print("没有需要保存的段子.")
            return
        filename = os.path.join(os.path.abspath(os.path.dirname(__file__)) , "stories.txt")
        print( "保存 %d 个段子到文件 %s" % (len(self.stories), filename))
        with codecs.open(filename, "w", "utf-8") as file:
            now = datetime.now()
            file.write('创建日期: %s 数量: %d\r\n\r\n' % (now.strftime('%Y-%m-%d %H:%M:%S'), len(self.stories)))
            for item in self.stories:
                file.write('作者: %s 好笑: %d 评论: %d\r\n' % (item.author, int(item.stats_vote_num), int(item.comments_num)))
                file.write('%s\r\n' % (item.content))
                #file.write('URL: %s\r\n' % (item.content_herf))
                if item.cmt_text != 'None':
                    file.write('神评作者: %s 评论: %s\r\n' % (item.cmt_name, item.cmt_text))
                file.write('\r\n')


def main():
    #print 'new encoding value:', sys.getdefaultencoding()
    #print "你好" == u"你好"
    spider = QSBK_Download()
    #获取全部段子
    spider.getAll()
    #保存到文件
    spider.save()
    pass

if __name__ == '__main__':
    main()
