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
from db.mongodb import MongoDB
from utils.log import log
import time

class Collector(threading.Thread):
    def __init__(self, tab_urls):
        super(Collector, self).__init__()
        self._lock = threading.RLock()

        self._db = MongoDB()
        self._thread_stop = False
        self._urls =[]
        self._null_times = 0
        self._tab_urls = tab_urls
        self._depth = int(tools.get_conf_value('config.conf', "collector", "depth"))
        self._max_size = int(tools.get_conf_value('config.conf', "collector", "max_size"))
        self._interval = int(tools.get_conf_value('config.conf', "collector", "sleep_time"))
        self._allowed_null_times = int(tools.get_conf_value('config.conf', "collector", 'allowed_null_times'))
        self._url_count = int(tools.get_conf_value('config.conf', "collector", "url_count"))

        #初始时将正在做的任务至为未做
        self._db.update(self._tab_urls, {'status':Constance.DOING}, {'status':Constance.TODO})

        self._finished_callback = None

    def run(self):
        while not self._thread_stop:
            self.__input_data()
            time.sleep(self._interval)

    def stop(self):
        self._thread_stop = True
        if self._finished_callback:
            self._finished_callback()

    # @tools.log_function_time
    def __input_data(self):
        if len(self._urls) > self._url_count:
            return

        urls_list = []
        if self._depth:
            urls_list = self._db.find(self._tab_urls, {"status":Constance.TODO, "depth":{"$lte":self._depth}}, limit = self._url_count)
        else:
            urls_list = self._db.find(self._tab_urls, {"status":Constance.TODO}, limit = self._url_count)

        #更新已取到的url状态为doing
        for url in urls_list:
            self._db.update(self._tab_urls, url, {'status':Constance.DOING})

        # 存url
        self.put_urls(urls_list)

        if self.is_all_have_done():
            print('is_all_have_done')
            self.stop()

    def is_finished(self):
        return self._thread_stop

    def add_finished_callback(self, callback):
        self._finished_callback = callback

    # 没有可做的url
    def is_all_have_done(self):
        print('判断是否有未做的url ')
        if len(self._urls) == 0:
            self._null_times += 1
            if self._null_times >= self._allowed_null_times:
                #检查数据库中有没有正在做的url
                urls_doing = self._db.find(self._tab_urls, {'status':Constance.DOING})
                if urls_doing: # 如果有未做的url 且数量有变化，说明没有卡死
                    print('有未做的url %s'%len(urls_doing))
                    self._null_times = 0
                    return False
                else:
                    return True
            else:
                return False
        else:
            self._null_times = 0
            return False


    # @tools.log_function_time
    def put_urls(self, urls_list):
        self._urls.extend(urls_list)

    # @tools.log_function_time
    def get_urls(self, count):
        self._lock.acquire() #加锁

        urls = self._urls[:count]
        del self._urls[:count]

        self._lock.release()

        return urls

if __name__ == '__main__':
    # collector = Collector('news_urls')
    # url = collector.get_urls(20)
    # print(url)
    pass