# -*- coding: utf-8 -*-
'''
Created on 2018-06-19 17:17
---------
@summary: url 管理器， 负责缓冲添加到数据库中的url， 由该manager统一添加。防止多线程同时访问数据库
---------
@author: Boris
'''
import sys
sys.path.append('..')
import init
import threading
import base.constance as Constance
import utils.tools as tools
from db.redisdb import RedisDB
from utils.log import log
import time
import collections

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls)

        return cls._inst

class UrlManager(threading.Thread, Singleton):
    def __init__(self, table_url = 'urls'):
        if not hasattr(self,'_table_url'):
            super(UrlManager, self).__init__()

            self._thread_stop = False

            self._urls_deque = collections.deque()
            self._db = RedisDB()
            self._table_url = table_url
            self._table_url_dupefilter = self._table_url + '_dupefilter'
            self._table_url_end_depth_dupefilter = self._table_url + '_end_depth_dupefilter'

    def run(self):
        while not self._thread_stop:
            self.__add_url_to_db()
            tools.delay_time(1)

    def stop(self):
        self._thread_stop = True

    def put_urls(self, urls):
        urls = urls if isinstance(urls, list) else [urls]
        for url in urls:
            self._urls_deque.append(url)

    def get_urls_count(self):
        return len(self._urls_deque)

    def clear_url(self):
        '''
        @summary: 删除redis里的数据
        ---------
        ---------
        @result:
        '''

        self._db.clear(self._table_url)
        self._db.clear(self._table_url_dupefilter)

    def __add_url_to_db(self):
        url_list = []
        while self._urls_deque:
            url = self._urls_deque.popleft()
            url_id = tools.get_sha1(url.get('url'))
            depth = url.get('depth', 0)
            max_depth = url.get('remark',{}).get('spider_depth', 0)
            if depth == max_depth - 1: #最后一层 url单独放，之后不需要清空
                if self._db.sadd(self._table_url_end_depth_dupefilter, url_id) and self._db.sadd(self._table_url_dupefilter, url_id):
                    url_list.append(url)

            elif self._db.sadd(self._table_url_dupefilter, url_id):
                url_list.append(url)

            if len(url_list) > 100:
                log.debug('添加url到数据库')
                self._db.lpush(self._table_url, url_list)
                url_list = []

        if url_list:
            log.debug('添加url到数据库')
            self._db.lpush(self._table_url, url_list)


if __name__ == '__main__':
    url_manager = UrlManager('dsfdsafadsf')
    # url_manager.start()

    urls = collections.deque()
    data = {
        "url": "http://www.icm9.com/",
        "status": 3213,
        "remark": {
            "spider_depth": 3,
            "website_name": "早间新闻",
            "website_position": 23,
            "website_domain": "icm9.com",
            "website_url": "http://www.icm9.com/"
        },
        "depth": 0,
        "_id": "5b15f33d53446530acf20539",
        "site_id": 1,
        "retry_times": 0
    }
    url_manager.put_urls(data)
    url_manager.put_urls(data)
    url_manager.put_urls(data)
    print(url_manager.get_urls_count())
