# -*- coding: utf-8 -*-
'''
Created on 2016-12-23 11:24
---------
@summary: url 管理器 负责取url 存储在环形的urls列表中
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
from base.url_manager import UrlManager
import collections

LOCAL_HOST_IP = tools.get_localhost_ip()

class Collector(threading.Thread):
    def __init__(self, tab_urls, depth):
        super(Collector, self).__init__()
        self._db = RedisDB()
        self._thread_stop = False
        self._urls = collections.deque()
        self._null_times = 0
        self._tab_urls = tab_urls
        self._depth = depth# or int(tools.get_conf_value('config.conf', "collector", "depth"))
        self._interval = int(tools.get_conf_value('config.conf', "collector", "sleep_time"))
        self._allowed_null_times = int(tools.get_conf_value('config.conf', "collector", 'allowed_null_times'))
        self._url_count = int(tools.get_conf_value('config.conf', "collector", "url_count"))

        self._url_manager = UrlManager(tab_urls)

        self._finished_callback = None

        self._is_show_wait = False

    def run(self):
        while not self._thread_stop:
            try:
                self.__input_data()
            except Exception as e:
                log.error(e)

            time.sleep(self._interval)

    def stop(self):
        self._thread_stop = True
        if self._finished_callback:
            self._finished_callback()

    # @tools.log_function_time
    def __input_data(self):
        if self._urls:
            log.debug('url 未处理完，不取url， url数量 = %s'%len(self._urls))
            return

        # 汇报节点信息
        self._db.zadd('news:worker_status', LOCAL_HOST_IP, 0) # 未做

        url_count = self._url_count # 先赋值
        # 根据等待节点数量，动态分配url
        worker_wait_count = self._db.zget_count('news:worker_status', priority_min = 0, priority_max = 0)
        if worker_wait_count:
            # 任务数量
            task_count = self._db.zget_count(self._tab_urls)
            # 动态分配的数量 = 任务数量 / 休息的节点数量
            url_count = task_count // worker_wait_count

        url_count = url_count if url_count <= self._url_count else self._url_count

        urls_list = self._db.zget(self._tab_urls, count = url_count)

        if not urls_list:
            if not self._is_show_wait:
                log.info('等待任务...')
                self._is_show_wait = True
        else:
            # 汇报节点信息
            self._db.zadd('news:worker_status', LOCAL_HOST_IP, 1) # 正在做

            # 存url
            self.put_urls(urls_list)
            self._is_show_wait = False

        # if self.is_all_have_done():
        #     log.debug('is_all_have_done end')
        #     self.stop()

    def is_finished(self):
        return self._thread_stop

    def add_finished_callback(self, callback):
        self._finished_callback = callback

    # 没有可做的url
    def is_all_have_done(self):
        # log.debug('判断是否有未做的url collector url size = %s | url_manager size = %s'%(len(self._urls), self._url_manager.get_urls_count()))
        if len(self._urls) == 0:
            self._null_times += 1
            if self._null_times >= self._allowed_null_times and self._url_manager.get_urls_count() == 0:
                return True
            else:
                return False
        else:
            self._null_times = 0
            return False


    # @tools.log_function_time
    def put_urls(self, urls_list):
        for url_info in urls_list:
            try:
                url_info = eval(url_info)
            except Exception as e:
                url_info = None

            if url_info:
                self._urls.append(url_info)

    # @tools.log_function_time
    def get_urls(self, count):
        urls = []
        count = count if count <= len(self._urls) else len(self._urls)
        while count:
            urls.append(self._urls.popleft())
            count -= 1

        return urls

if __name__ == '__main__':
    # collector = Collector('news_urls')
    # url = collector.get_urls(20)
    # print(url)
    print(LOCAL_HOST_IP)
    pass

