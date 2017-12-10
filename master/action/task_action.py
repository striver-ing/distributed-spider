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
        print(name)
        print(data)

        if name == 'get_task':
            tasks = self.task_service.get_task()
            return tools.dumps_json(tasks)

        elif name == 'update_task':
            tasks = eval(data.get('tasks', []))
            status = data.get('status')
            self.task_service.update_task_status(tasks, status)

            return tools.dumps_json('{"status":1}')

    def GET(self, name):
        return self.deal_request(name)

    def POST(self, name):
        return self.deal_request(name)

