# -*- coding: utf-8 -*-
'''
Created on 2017-08-02 09:20
---------
@summary: 配置
---------
@author: Boris
'''

# url映射配置


# Turn on/off debugging
DEBUG = False

URLS = (
    '/task(.*)', 'action.task_action.TaskAction',
    '/(.*)', 'action.help.Help'
)

API_PORT = 9306