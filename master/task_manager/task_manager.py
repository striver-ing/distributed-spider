# -*- coding: utf-8 -*-
'''
Created on 2017-12-08 11:35
---------
@summary: 任务分发器
---------
@author: Boris
'''
import sys
sys.path.append('..')
import init

import utils.tools as tools
from db.oracledb import OracleDB
from db.redisdb import RedisDB
from utils.log import log

ONE_PAGE_SIZE = 1000 # 一次取的任务数
CHECK_HAVE_TASK_SLEEP_TIME = 10
MAX_NULL_TASK_TIME =10 * 60  # 连续n秒内task队列都为空，则视为跑完一轮


class TaskManager():
    def __init__(self):
        self._oracledb = OracleDB()
        self._redisdb = RedisDB()
        self._news_url_table = 'news:news_urls'
        self._news_urls_dupefilter = 'news:news_urls_dupefilter'

    def is_have_task(self):
        '''
        @summary: redis 中是否有待做的url
        ---------
        ---------
        @result:
        '''

        return self._redisdb.lget_count(self._news_url_table)

    def get_task_from_oracle(self):
        tasks = []

        offset = 0
        while True:
            # 取任务
            task_sql = '''
                select *
                  from (select t.id, t.name, t.position, t.url, t.depth, rownum r
                          from TAB_IOPM_SITE t
                         where classify = 1
                           and t.mointor_status = 701
                           and (t.position != 35 or t.position is null)
                           and rownum < {page_size})
                 where r >= {offset}
            '''.format(page_size = offset + ONE_PAGE_SIZE, offset = offset)

            results = self._oracledb.find(task_sql)
            offset += ONE_PAGE_SIZE

            if not results: break

            # 拼装成json格式的url
            for task in results:
                website_id = task[0]
                website_name = task[1]
                website_position = task[2]
                website_url = task[3]
                website_domain = tools.get_domain(website_url)
                spider_depth = task[4]

                remark = {'website_name':website_name, 'website_position':website_position, 'website_url': website_url, 'website_domain':website_domain, 'spider_depth':spider_depth}
                url_dict = {'site_id':1, 'url':website_url, 'depth': 0, 'remark':remark, 'retry_times' : 0}

                tasks.append(url_dict)

        return tasks

    def add_task_to_redis(self, tasks):
        for task in tasks:
            url = task.get('url')
            if url:
                url_id = tools.get_sha1(url)
                if self._redisdb.sadd(self._news_urls_dupefilter, url_id):
                    self._redisdb.lpush(self._news_url_table, task)

    def clear_task(self):
        # 清空url指纹表
        self._redisdb.clear('news:news_urls_dupefilter')

def monitor_task():
    task_manager = TaskManager()
    total_time = 0
    while True:
        is_have_task = task_manager.is_have_task()
        if not is_have_task:
            log.debug('redis 中连续%s秒无任务， 休眠%s秒后再检查'%(total_time, CHECK_HAVE_TASK_SLEEP_TIME))
            total_time += CHECK_HAVE_TASK_SLEEP_TIME
            tools.delay_time(CHECK_HAVE_TASK_SLEEP_TIME)
        else:
            total_time = 0
            tools.delay_time(CHECK_HAVE_TASK_SLEEP_TIME)

        if total_time > MAX_NULL_TASK_TIME:
            log.debug('redis 中连续%s秒无任务，超过允许最大等待%s秒 开始添加任务'%(total_time, MAX_NULL_TASK_TIME))
            # 删除url指纹
            task_manager.clear_task()
            # 取任务
            tasks = task_manager.get_task_from_oracle()
            if tasks:
                task_manager.add_task_to_redis(tasks)
                task_count = task_manager.is_have_task()
                if task_count:
                    log.debug('添加任务到redis中成功 共添加%s条任务。 work开始工作'%(task_count))
            else:
                log.error('未从oracle中取到任务')

if __name__ == '__main__':
    monitor_task()
    # task_manager = TaskManager()
    # task = task_manager.get_task_from_oracle()
    # task_count = task_manager.is_have_task()
    # print(task_count)

