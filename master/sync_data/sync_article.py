# -*- coding: utf-8 -*-
'''
Created on 2018-07-03 15:42
---------
@summary: 同步redis中的数据到es
---------
@author: Boris
'''

import sys
sys.path.append('../')
import init
from db.redisdb import RedisDB
from db.elastic_search import ES
import threading
import utils.tools as tools
from utils.log import log

SYNC_STEP = 500 # 一次同步的数据量

class SyncArtice(threading.Thread):
    def __init__(self):
        super(SyncArtice, self).__init__()

        self._es = ES()
        self._redis = RedisDB()
        self._sync_count = 0

    def run(self):
        is_show_tip = False
        while True:
            try:
                datas = self.get_data_from_redis(SYNC_STEP)
                if not datas:
                    if not is_show_tip:
                        print('\n{time} 无数据 休眠...    '.format(time = tools.get_current_date()))
                        is_show_tip = True
                elif self.add_data_to_es(datas):
                    is_show_tip = False
                    self._sync_count += len(datas)
                    tools.print_one_line('已同步 %d 条数据'%self._sync_count)
                tools.delay_time(1)
            except Exception as e:
                log.error(e)

    def get_data_from_redis(self, count):
        datas = self._redis.sget('news:news_article', count = count)
        return_datas = []
        for data in datas:
            data = eval(data)
            release_time = data.get('release_time')
            if release_time and len(release_time) == 19:
                return_datas.append(data)

        return return_datas

    def add_data_to_es(self, datas):
        return self._es.add_batch(datas, primary_key = 'uuid', table = 'news_article')


if __name__ == '__main__':
    sync_article = SyncArtice()
    sync_article.start()
