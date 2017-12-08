# -*- coding: utf-8 -*-
'''
Created on 2017-12-06 10:13
---------
@summary:
---------
@author: Boris
'''
import sys
sys.path.append('..')
import init

import requests
import base.constance as Constance
import random

# http://localhost:8000/
class NetWork():
    def __init__(self):
        self.browser_user_agent = self.get_user_agent()
        self.headers = {}
        self.request_timeout = 7
        self.proxies = self.get_proxies()

    def get_proxies(self):
        '''
        @summary: 获取 需要运行IPPProxyPool
        ---------
        @param :
        ---------
        @result:
        '''

        try:
            reponse = requests.get('http://127.0.0.1:8000/?types=0&count=50')
            proxies = reponse.json()
            proxie = random.choice(proxies)

            ip = proxie[0]
            port = proxie[1]

            return {'http':"http://{ip}:{port}".format(ip = ip, port = port), 'https':"https://{ip}:{port}".format(ip = ip, port = port)}

        except:
            return {}
        finally:
            if reponse: reponse.close()


    def get_user_agent(self):
        try:
            return  random.choice(Constance.USER_AGENTS)
        except:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"

if __name__ == '__main__':
    network = NetWork()
    print(network.browser_user_agent)
    print(network.proxies)