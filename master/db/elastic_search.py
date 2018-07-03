# -*- coding: utf-8 -*-
'''
Created on 2017-08-22 14:06
---------
@summary: 同步oracle数据库到ElasticSearc
---------
@author: Boris
'''

import sys
sys.path.append('../')
import init
import utils.tools as tools
from elasticsearch import Elasticsearch
import elasticsearch.helpers
from utils.log import log

ADDRESS = tools.get_conf_value('config.conf', 'elasticsearch', 'address')

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls)

        return cls._inst

class ES():
    def __init__(self, address = ADDRESS):
        try:
            print(address.split(','))
            self._es = Elasticsearch(address.split(','))
        except Exception as e:
            raise
        else:
            log.debug('连接到Elasticsearch')

    def add(self, table, data, data_id = None, doc_type = ''):
        '''
        @summary:
        ---------
        @param table: 索引
        @param data_json: 数据 json类型
        @param doc_type: 类型 空时以表命名。 doc_type可理解为同样的数据结构不同意意义。比如url表，doc_type 可以以网站名命名
        @param data_id data_id不指定，会自己创建， data_id已存在，则更新
        ---------
        @result:
        '''
        try:
            table = table.lower()
            self._es.index(index = table, doc_type = doc_type or table ,id = data_id, body = data)
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def add_batch(self, datas, primary_key, table, doc_type =  ''):
        try:
            actions = [
                {
                    '_op_type': 'index',
                    '_index': table,
                    '_type': doc_type or table,
                    # '_score':1,
                    '_id':data[primary_key],
                    '_source': data
                }
                for data in datas
            ]

            elasticsearch.helpers.bulk(self._es, actions)

        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def get(self, table, data_id, doc_type = '_all'):
        '''
        @summary: 根据id取数据
        ---------
        @param table:索引
        @param data_id:数据id 如 ID=1 的数据
        @param doc_type:类型 _all 为全部
        ---------
        @result: json
        '''
        datas = {}

        try:
            table = table.lower()
            datas = self._es.get(index = table, doc_type = doc_type, id = data_id)

        except Exception as e:
            # log.error(e)
            pass

        return datas


    def search(self, table, body = {}):
        '''
        @summary:
        ---------
        @param table:
        @param body: 查询条件
        ---------
        @result: json
        '''

        datas = {}

        try:
            table = table.lower()
            datas = self._es.search(index = table, body = body, request_timeout = 30)

        except Exception as e:
            log.error(e)

        return datas

    def update_by_id(self, table, data_id, data, doc_type = ''):
        '''
        @summary:
        ---------
        @param table:
        @param data_id:
        @param data: {"TITLE":"xxx"} 更新的字段及值
        @param doc_type:
        ---------
        @result:
        '''
        try:
            self._es.update(index = table, doc_type = doc_type or table, body = {"doc": data}, id = data_id)
        except Exception as e:
            log.debug(e)
            return False

        return True

    def delete_by_id(self, table, data_id, doc_type = ''):
        """
        根据给定的id,删除文档
        :return:
        """

        try:
            self._es.delete(index = table, doc_type = doc_type or table, id = data_id)
        except Exception as e:
            log.debug(e)
            return False

        return True


    def set_mapping(self, table, mapping, doc_type):
        '''
        @summary:
        ---------
        @param table:
        @param mapping:
        mapping = {
            self.doc_type: {
                "properties": {
                    "document_id": {
                        "type": "integer"
                    },
                    "title": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    }
                }
            }
        }
        @param doc_type:
        ---------
        @result:
        '''

        if not self._es.indices.exists(index = table):
            # 创建Index和mapping
            self._es.indices.create(index = table, body = mapping, ignore=400)
            self._es.indices.put_mapping(index = table, doc_type = doc_type or table, body = mapping)

if __name__ == '__main__':
    es = ES()
