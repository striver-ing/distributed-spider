# -*- coding: utf-8 -*-
'''
Created on 2017-01-03 11:05
---------
@summary: 提供一些操作数据库公用的方法
---------
@author: Boris
'''
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

if __name__ == '__main__':
    set_mapping()
    pass