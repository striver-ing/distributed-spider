# -*- coding: utf-8 -*-
'''
Created on 2017-12-06 10:13
---------
@summary:
---------
@author: Boris
'''

class NetWork():
    def __init__(self):
        self.browser_user_agent = ''
        self.headers = {}
        self.request_timeout = 7
        self.proxies = {}