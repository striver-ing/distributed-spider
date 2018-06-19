# -*- coding: utf-8 -*-
'''
Created on 2017-12-08 13:52
---------
@summary:
---------
@author: Boris
'''
import sys
sys.path.append('..')

from utils.log import log
import utils.tools as tools
import web
import json
from service.task_service import TaskService

class TaskAction():
    def __init__(self):
        self.task_service = TaskService()

    def deal_request(self, name):
        web.header('Content-Type','text/html;charset=UTF-8')

        data = json.loads(json.dumps(web.input()))
        client_ip = web.ctx.ip

        if name == 'get_task':
            tasks = self.task_service.get_task()
            tasks = tools.dumps_json(tasks)
            log.info('''
                客户端 ip: %s
                取任务   : %s'''%(client_ip, tasks))

            return tasks

        elif name == 'update_task':
            tasks = eval(data.get('tasks', []))
            status = data.get('status')
            self.task_service.update_task_status(tasks, status)

            return tools.dumps_json('{"status":1}')

    def GET(self, name):
        return self.deal_request(name)

    def POST(self, name):
        return self.deal_request(name)

