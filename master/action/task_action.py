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

    def deal_request(self):
        web.header('Content-Type','text/html;charset=UTF-8')

        # data = json.loads(json.dumps(web.input()))
        # print(data)
        tasks = self.task_service.get_task()

        return tools.dumps_json(tasks)

    def GET(self):
        return self.deal_request()

    def POST(self):
        return self.deal_request()

