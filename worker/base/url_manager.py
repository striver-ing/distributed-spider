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

MAX_URL_COUNT = 10000 # 缓存中最大url数

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
            try:
                self.__add_url_to_db()
            except Exception as e:
                log.error(e)

            log.debug('缓存url数量 %s'%len(self._urls_deque))
            tools.delay_time(1)

    def stop(self):
        self._thread_stop = True

    def put_urls(self, urls):
        urls = urls if isinstance(urls, list) else [urls]
        for url in urls:
            self._urls_deque.append(url)

        if self.get_urls_count() > MAX_URL_COUNT: # 超过最大缓存，总动调用
            self.__add_url_to_db()

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

    def print_url(self, i):
        while self._urls_deque:
            url = self._urls_deque.popleft()
            print(i, '-->', url)

    def __add_url_to_db(self):
        url_list = []
        prioritys = []

        while self._urls_deque:
            url = self._urls_deque.popleft()
            url_id = tools.get_sha1(url.get('url'))
            depth = url.get('depth', 0)

            max_depth = url.get('remark',{}).get('spider_depth', 0)
            if depth == max_depth - 1: #最后一层 url单独放，之后不需要清空
                if self._db.sadd(self._table_url_end_depth_dupefilter, url_id) and self._db.sadd(self._table_url_dupefilter, url_id):
                    url_list.append(url)
                    prioritys.append(depth)
                    # 统计每层的url数量，将url_id添加到每层的表，不做统计时可注释掉
                    self._db.sadd(self._table_url_dupefilter + str(depth), url_id)

            elif self._db.sadd(self._table_url_dupefilter, url_id):
                url_list.append(url)
                prioritys.append(depth)
                # 统计每层的url数量，将url_id添加到每层的表，不做统计时可注释掉
                self._db.sadd(self._table_url_dupefilter + str(depth), url_id)

            if len(url_list) > 100:
                log.debug('添加url到数据库')
                self._db.zadd(self._table_url, url_list, prioritys)
                url_list = []
                prioritys = []

        if url_list:
            log.debug('添加url到数据库')
            self._db.zadd(self._table_url, url_list, prioritys)


if __name__ == '__main__':
    url_manager = UrlManager('dsfdsafadsf')

    for i in range(100):
        url_manager.put_urls(i)

    for i in range(5):
        threading.Thread(target = url_manager.print_url, args = (i, )).start()
