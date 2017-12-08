# -*- coding: utf-8 -*-
'''
Created on 2017-01-03 11:05
---------
@summary: 提供一些操作数据库公用的方法
---------
@author: Boris
'''
import sys
sys.path.append('..')
import init

import base.constance as Constance
import utils.tools as tools
from db.mongodb import MongoDB
import random

db = MongoDB()

def get_contained_key(title, content, key1, key2, key3):
    text = title + content

    # 过滤
    if tools.get_info(text, key3):
        return '', 0

    # 取包含的关键字
    contained_key = []
    contained_key_count = 0

    def get_weigth(text, keys, key_weigth):
        weigth = 0
        contained_key = []

        for key in keys:
            for cut_key in cut_text.cut_for_keyword(key):
                if cut_key.lower() in text.lower():
                    weigth += key_weigth
                    contained_key.append(cut_key)

        return weigth, contained_key

    # 判断标题
    # 标题中包含key1 权重+ 125
    result = get_weigth(title, key1, 125)
    contained_key_count += result[0]
    contained_key.extend(result[1])
    # 标题中包含key2 权重+ 25
    result = get_weigth(title, key2, 25)
    contained_key_count += result[0]
    contained_key.extend(result[1])

    # 判断内容
    # 内容中包含key1 权重+ 5
    result = get_weigth(content, key1, 5)
    contained_key_count += result[0]
    contained_key.extend(result[1])
    # 内容中包含key2 权重+ 1
    result = get_weigth(content, key2, 1)
    contained_key_count += result[0]
    contained_key.extend(result[1])

    return ','.join(contained_key), contained_key_count

def is_violate(content, key1 = [], key2 = [], key3 =[]):
    if not key1 and not key2:
        return False

    def check_key1(keys, content):
        for key in keys:
            key = key.strip() if key else ''
            if not key:
                continue

            if key not in content:
                return False
        else:
            return True

    def check_key2(keys, content):
        for key in keys:
            key = key.strip() if key else ''
            if not key:
                continue

            if key in content:
                return True
        else:
            return False

    def check_key3(keys, content):
        for key in keys:
            key = key.strip() if key else ''
            if not key:
                continue

            if key in content:
                return False
        else:
            return True

    result = True

    if key1:
        result = check_key1(key1, content)
    if key2:
        result = result and check_key2(key2, content)
    if key3:
        result = result and check_key3(key3, content)

    return result

def get_proxies():
    '''
    @summary: 获取 需要运行IPPProxyPool
    ---------
    @param :
    ---------
    @result:
    '''

    try:
        proxies, r = tools.get_html_by_requests('http://127.0.0.1:8000/?types=0&count=50')
        proxies = eval(proxies)
        proxie = random.choice(proxies)

        ip = proxie[0]
        port = proxie[1]

        return {'http':"http://{ip}:{port}".format(ip = ip, port = port), 'https':"https://{ip}:{port}".format(ip = ip, port = port)}

    except:
        return {}

def get_user_agent():
    try:
        return  random.choice(Constance.USER_AGENTS)
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"

def get_site_id(table, site_name):
    result = db.find(table, {'name':site_name})
    if result:
        return result[0]['site_id']
    else:
        raise AttributeError('%s表中无%s信息'%(table, site_name))

def add_url(table, site_id, url, depth = 0, remark = '', status = Constance.TODO, retry_times = 0):
    url_dict = {'site_id':site_id, 'url':url, 'depth':depth, 'remark':remark, 'status':status, 'retry_times' : retry_times}
    return db.add(table, url_dict)

def update_url(table, url, status, retry_times = 0):
    db.update(table, {'url':url}, {'status':status, 'retry_times':retry_times})

def add_website_info(table, site_id, url, name, domain = '', ip = '', address = '', video_license = '', public_safety = '', icp = ''):
    '''
    @summary: 添加网站信息
    ---------
    @param table: 表名
    @param site_id: 网站id
    @param url: 网址
    @param name: 网站名
    @param domain: 域名
    @param ip: 服务器ip
    @param address: 服务器地址
    @param video_license: 网络视听许可证|
    @param public_safety: 公安备案号
    @param icp: ICP号
    ---------
    @result:
    '''

    # 用程序获取domain,ip,address,video_license,public_safety,icp 等信息
    domain = tools.get_domain(url)

    site_info = {
        'site_id':site_id,
        'name':name,
        'domain':domain,
        'url':url,
        'ip':ip,
        'address':address,
        'video_license':video_license,
        'public_safety':public_safety,
        'icp':icp,
        'read_status':0,
        'record_time': tools.get_current_date()
    }
    db.add(table, site_info)

