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
import configparser #读配置文件的
import codecs

def get_conf_value(config_file, section, key):
    cp = configparser.ConfigParser(allow_no_value = True)
    with codecs.open(config_file, 'r', encoding='utf-8') as f:
        cp.read_file(f)
    return cp.get(section, key)

IPPROXY_ADDRESS = get_conf_value('config.conf', 'ipproxy', 'address')

class NetWork():
    def __init__(self):
        self.browser_user_agent = ''#self.get_user_agent()
        self.headers = {}
        self.request_timeout = 7
        self.proxies = {}#self.get_proxies()

    def get_proxies(self):
        '''
        @summary: 获取 需要运行IPPProxyPool
        ---------
        @param :
        ---------
        @result:
        '''
        reponse = ''
        try:
            reponse = requests.get(IPPROXY_ADDRESS)
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