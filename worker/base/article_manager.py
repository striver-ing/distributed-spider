# -*- coding: utf-8 -*-
'''
Created on 2018-06-19 17:17
---------
@summary: article 管理器， 负责缓冲添加到数据库中的article， 由该manager统一添加。防止多线程同时访问数据库
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
from utils.bloomfilter import BloomFilter

MAX_ARTICLE_COUNT = 500 # 缓存中最大文章数

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls)

        return cls._inst

class ArticleManager(threading.Thread, Singleton):
    def __init__(self, table_article = 'articles'):
        if not hasattr(self,'_table_article'):
            super(ArticleManager, self).__init__()

            self._thread_stop = False

            self._articles_deque = collections.deque()
            self._db = RedisDB()
            self._table_article = table_article
            self._table_article_bloomfilter = table_article + '_bloomfilter'

            self._bloomfilter = BloomFilter(redis_obj = self._db, key = self._table_article_bloomfilter)

    def run(self):
        while not self._thread_stop:
            try:
                self.__add_article_to_db()
            except Exception as e:
                log.error(e)

            log.debug('缓存中文章数量 %s'%len(self._articles_deque))
            tools.delay_time(1)

    def stop(self):
        self._thread_stop = True

    def put_articles(self, article):
        self._articles_deque.append(article)

        if self.get_articles_count() > MAX_ARTICLE_COUNT: # 超过最大缓存，总动调用
            self.__add_article_to_db()

    def get_articles_count(self):
        return len(self._table_article)

    def clear_article(self):
        '''
        @summary: 删除redis里的数据
        ---------
        ---------
        @result:
        '''

        self._db.clear(self._table_article)

    def __add_article_to_db(self):
        article_list = []
        while self._articles_deque:
            article = self._articles_deque.popleft()
            # 查看article是否存在
            if self._bloomfilter.is_contains(article.get('uuid')):
                article_list.append(article)
            else:
                self._bloomfilter.insert(article.get('uuid'))

            if len(article_list) > 100:
                log.debug('添加article到数据库')
                self._db.sadd(self._table_article, article_list)
                article_list = []

        if article_list:
            log.debug('添加article到数据库')
            self._db.sadd(self._table_article, article_list)


if __name__ == '__main__':
    article_manager = ArticleManager('dsfdsafadsf')
