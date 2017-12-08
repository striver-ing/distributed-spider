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

def set_mapping():
    mapping = {
        "news_article":{
            "properties":{
                "website":{
                    "type":"string",
                    "analyzer":"ik_max_word"
                },
                "author":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "domain":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "position":{
                    "type":"long"
                },
                "title":{
                    "type":"string",
                    "analyzer":"ik_max_word"
                },
                "uuid":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "content":{
                    "type":"string",
                    "analyzer":"ik_max_word"
                },
                "url":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "release_time":{
                    "type":"date",
                    "format":"yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                },
                "record_time":{
                    "type":"date",
                    "format":"yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                }
            }
        }
    }

    es.set_mapping('news_article', mapping)

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


if __name__ == '__main__':
    set_mapping()