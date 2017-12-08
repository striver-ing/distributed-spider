# -*- coding: utf-8 -*-
'''
Created on 2017-01-03 13:40
---------
@summary: 初始化工作
---------
@author: Boris
'''

# 添加搜索路经
import os
import sys

PROJECT_NAME = 'worker'

current_path = os.getcwd()
project_path = current_path[:current_path.find(PROJECT_NAME) + len(PROJECT_NAME)]

os.chdir(project_path) # 切换工作路经
sys.path.append(project_path)