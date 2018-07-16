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
from utils.log import get_logger
import manager.statistic_article_count as statistic_article_count
import os

PROJECT_PATH = os.getcwd()
PROJECT_NAME = PROJECT_PATH[PROJECT_PATH.rfind('\\') + 1:]
log = get_logger(name = 'task_manager.log', path = PROJECT_PATH + '\\log\\')

ONE_PAGE_SIZE = 1000 # 一次取的任务数
CHECK_HAVE_TASK_SLEEP_TIME = 10
MAX_NULL_TASK_TIME =10 * 60  # 连续n秒内task队列都为空，则视为跑完一轮

class TaskManager():
    def __init__(self):
        self._oracledb = OracleDB()
        self._redisdb = RedisDB()
        self._news_url_table = 'news:news_urls'
        self._news_urls_dupefilter = 'news:news_urls_dupefilter'

    def get_task_count(self):
        '''
        @summary: redis 中是否有待做的url
        ---------
        ---------
        @result:
        '''

        return self._redisdb.zget_count(self._news_url_table)

    def get_ever_depth_count(self, total_depth = 5):
        '''
        @summary:
        ---------
        @param total_depth: 不包含。 以客户角度的层数
        ---------
        @result:
        '''

        depth_count_info = {}
        total_count = 0
        for depth in range(total_depth):
            key = '第%s层url数'% (depth + 1)
            depth_count_info[key] = self._redisdb.sget_count(self._news_urls_dupefilter  + str(depth))
            total_count += depth_count_info[key]

        depth_count_info['总url数'] = total_count
        return depth_count_info

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
                    self._redisdb.zadd(self._news_url_table, task, prioritys = 0)
                    # 下面是统计每层url数量用的表
                    self._redisdb.sadd('news:news_urls_dupefilter0', url_id)

    def clear_task(self):
        # 清空url指纹表
        self._redisdb.sdelete('news:news_urls_dupefilter')
        # 下面是统计每层url数量用的表
        self._redisdb.sdelete('news:news_urls_dupefilter0')
        self._redisdb.sdelete('news:news_urls_dupefilter1')
        self._redisdb.sdelete('news:news_urls_dupefilter2')
        self._redisdb.sdelete('news:news_urls_dupefilter3')
        self._redisdb.sdelete('news:news_urls_dupefilter4')

def monitor_task():
    task_manager = TaskManager()
    total_time = 0

    task_count = 0
    begin_time = None
    end_time = None
    spend_hours = None

    is_show_start_tip = False
    is_show_have_task = False

    while True:
        task_count = task_manager.get_task_count()
        if not task_count:
            if not is_show_start_tip:
                log.info('开始监控任务池...')
                is_show_start_tip =  True

            total_time += CHECK_HAVE_TASK_SLEEP_TIME
            tools.delay_time(CHECK_HAVE_TASK_SLEEP_TIME)
        else:
            if not is_show_have_task:
                log.info('任务池中有%s条任务，work可以正常工作'%task_count)
                is_show_have_task = True

            total_time = 0
            tools.delay_time(CHECK_HAVE_TASK_SLEEP_TIME)

        if total_time > MAX_NULL_TASK_TIME:
            is_show_start_tip = False
            is_show_have_task = False

            # 结束一轮 做些统计
            if begin_time:
                # 统计时间
                end_time = tools.timestamp_to_date(tools.get_current_timestamp() - MAX_NULL_TASK_TIME)
                spend_time = tools.date_to_timestamp(end_time) - tools.date_to_timestamp(begin_time)
                spend_hours = tools.seconds_to_h_m_s(spend_time)

                # 统计url数量
                depth_count_info = task_manager.get_ever_depth_count(5)

                # 统计文章数量
                article_count_msg = statistic_article_count.get_article_count_msg(begin_time, end_time)

                log.info('''
                    ------- 已做完一轮 --------
                    \r开始时间：%s
                    \r结束时间：%s
                    \r耗时：%s
                    \r网站数量：%s
                    \rurl数量信息：%s
                    \r文章数量信息：%s
                    '''%(begin_time, end_time, spend_hours, task_count, tools.dumps_json(depth_count_info), article_count_msg))

            # 删除url指纹
            log.info('删除url指纹...')
            task_manager.clear_task()

            log.info('redis 中连续%s秒无任务，超过允许最大等待%s秒 开始添加任务'%(total_time, MAX_NULL_TASK_TIME))
            # 取任务
            tasks = task_manager.get_task_from_oracle()
            if tasks:
                total_time = 0
                task_manager.add_task_to_redis(tasks)
                task_count = task_manager.get_task_count()
                if task_count:
                    begin_time = tools.get_current_date()
                    log.info('添加任务到redis中成功 共添加%s条任务。 work开始工作'%(task_count))
            else:
                log.error('未从oracle中取到任务')

if __name__ == '__main__':
    monitor_task()
    # task_manager = TaskManager()
    # task_manager.clear_task()
    # depth_count_info = task_manager.get_ever_depth_count(5)
    # print(depth_count_info)
    # task = task_manager.get_task_from_oracle()
    # task_count = task_manager.get_task_count()
    # print(task_count)