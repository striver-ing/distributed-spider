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
        self._urls = []
        self._null_times = 0
        self._read_pos = -1
        self._write_pos = -1
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
        # log.debug('read_pos %d, write_pos %d buffer size %d'%(self._read_pos, self._write_pos, self.get_max_read_size()))
        # log.debug('buffer can write size = %d'%self.get_max_write_size())
        if self.get_max_write_size() == 0:
            log.debug("collector 已满 size = %d"%self.get_max_read_size())
            return

        url_count = self._url_count if self._url_count <= self.get_max_write_size() else self.get_max_write_size()

        urls_list = []
        if self._depth:
            urls_list = self._db.find(self._tab_urls, {"status":Constance.TODO, "depth":{"$lte":self._depth}}, limit = url_count)
        else:
            urls_list = self._db.find(self._tab_urls, {"status":Constance.TODO}, limit = url_count)

        #更新已取到的url状态为doing
        for url in urls_list:
            self._db.update(self._tab_urls, url, {'status':Constance.DOING})

        # 存url
        self.put_urls(urls_list)

        if self.is_all_have_done():
            self.stop()

    def is_finished(self):
        return self._thread_stop

    def add_finished_callback(self, callback):
        self._finished_callback = callback

    # 没有可做的url
    def is_all_have_done(self):
        if self.get_max_read_size() == 0:
            self._null_times += 1
            if self._null_times >= self._allowed_null_times:
                #检查数据库中有没有正在做的url
                urls_doing = self._db.find(self._tab_urls, {'status':Constance.DOING})
                if urls_doing:
                    self._null_times = 0
                    return False
                else:
                    return True
        else:
            self._null_times = 0
            return False

    def get_max_write_size(self):
        size = 0
        if self._read_pos == self._write_pos:
            size = self._max_size
        elif self._read_pos < self._write_pos:
            size = self._max_size - (self._write_pos - self._read_pos)
        else:
            size = self._read_pos - self._write_pos

        return size - 1

    def get_max_read_size(self):
        return self._max_size -1 - self.get_max_write_size()

    # @tools.log_function_time
    def put_urls(self, urls_list):
        # urls_list = urls_list[:self.get_max_write_size()]
        if urls_list == []:
            return

        # 添加url 到 _urls
        url_count = len((urls_list))
        end_pos = url_count + self._write_pos + 1
        # 判断是否超出队列容量 超出的话超出的部分需要从头写
        # 超出部分
        overflow_end_pos = end_pos - self._max_size
        # 没超出部分
        in_pos =  end_pos if end_pos <= self._max_size else self._max_size

        # 没超出部分的数量
        urls_listCutPos = in_pos - self._write_pos - 1

        self._lock.acquire() #加锁

        self._urls[self._write_pos + 1 : in_pos] = urls_list[:urls_listCutPos]
        if overflow_end_pos > 0:
            self._urls[:overflow_end_pos] = urls_list[urls_listCutPos:]

        self._lock.release()

        self._write_pos += url_count
        self._write_pos %= self._max_size   # -1 取余时问题  -1 % 1000 = 999  这样can write size 为0 urls_list为空时返回 规避了这个问题

    # @tools.log_function_time
    def get_urls(self, count):
        self._lock.acquire() #加锁
        urls = []

        count = count if count <= self.get_max_read_size() else self.get_max_read_size()
        end_pos = self._read_pos + count + 1
        if end_pos > self._max_size:
            urls.extend(self._urls[self._read_pos + 1:])
            urls.extend(self._urls[: end_pos % self._max_size])
        else:
            urls.extend(self._urls[self._read_pos + 1: end_pos])

        if urls:
            self._read_pos += len(urls)
            self._read_pos %= self._max_size

        self._lock.release()

        return urls