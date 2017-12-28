# -*- coding: utf-8 -*-
'''
Created on 2017-01-03 11:05
---------
@summary: 提供一些操作数据库公用的方法
---------
@author: Boris
'''
import sys
sys.path.append('../../')
import init

import utils.tools as tools
from db.elastic_search import ES

es = ES()

def add_news_acticle(uuid, title, author, release_time, website_name, website_domain, website_position, url, content):
    article = {
        'uuid' : uuid,
        'title' : title,
        'author' : author,
        'release_time' : release_time,
        'website' : website_name,
        'domain' : website_domain,
        'position' : website_position,
        'url' : url,
        'content' : content,
        'record_time' : tools.get_current_date()
    }

    es.add('news_article', article, uuid)