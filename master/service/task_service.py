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

import threading
import utils.tools as tools
from db.oracledb import OracleDB
from utils.log import log
from utils.ring_buff import RingBuff

TASK_BUFFER_SIZE = int(tools.get_conf_value('config.conf', 'task', 'task_buffer_size'))
TASK_COUNT = int(tools.get_conf_value('config.conf', 'task', 'task_count'))

class TaskService():
    _task_ring_buff = RingBuff(TASK_BUFFER_SIZE)
    _db = OracleDB()

    _offset = 1

    def __init__(self ):
        pass

    def load_task(self):
        task_sql = '''
            select *
              from (select t.id, t.name, t.position, t.url, t.domain, rownum r
                      from TAB_IOPM_SITE t
                     where position = 11
                       and classify = 1
                       and t.mointor_status = 701
                       and rownum < {page_size})
             where r >= {offset}
        '''.format(page_size = TaskService._offset + TASK_BUFFER_SIZE, offset = TaskService._offset)
        TaskService._offset += TASK_BUFFER_SIZE

        tasks = TaskService._db.find(task_sql)
        if not tasks:
            TaskService._offset = 1
            self.load_task()

        TaskService._task_ring_buff.put_data(tasks)

    def get_task(self, count = TASK_COUNT):
        tasks = TaskService._task_ring_buff.get_data(count)
        if not tasks:
            self.load_task()
            tasks = TaskService._task_ring_buff.get_data(count)

        return tasks


