# -*- coding: utf-8 -*-
'''
Created on 2016-11-16 16:25
---------
@summary: 操作redis数据库
---------
@author: Boris
'''
import sys
sys.path.append('../')
import init
import redis
import utils.tools as tools
from utils.log import log

IP        = tools.get_conf_value('config.conf', 'redis', 'ip')
PORT      = int(tools.get_conf_value('config.conf', 'redis', 'port'))
DB        = int(tools.get_conf_value('config.conf', 'redis', 'db'))
USER_PASS = tools.get_conf_value('config.conf', 'redis', 'user_pass')

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls, *args, **kwargs)

        return cls._inst


class RedisDB():
    def __init__(self, ip = IP, port = PORT, db = DB, user_pass = USER_PASS):
        # super(RedisDB, self).__init__()

        if not hasattr(self,'_redis'):
            try:
                self._redis = redis.Redis(host = ip, port = port, db = db, password = user_pass, decode_responses=True) # redis默认端口是6379
                self._pipe = self._redis.pipeline(transaction=True) # redis-py默认在执行每次请求都会创建（连接池申请连接）和断开（归还连接池）一次连接操作，如果想要在一次请求中指定多个命令，则可以使用pipline实现一次请求指定多个命令，并且默认情况下一次pipline 是原子性操作。

            except Exception as e:
                raise
            else:
                log.debug('连接到redis数据库 ip:%s  port:%s'%(ip, port))

    def sadd(self, table, values):
        '''
        @summary: 使用无序set集合存储数据， 去重
        ---------
        @param table:
        @param values: 值； 支持list 或 单个值
        ---------
        @result: 若库中存在 返回0，否则入库，返回1。 批量添加返回None
        '''

        if isinstance(values, list):
            self._pipe.multi()
            for value in values:
                self._pipe.sadd(table, value)
            self._pipe.execute()

        else:
            return self._redis.sadd(table, values)

    def zadd(self, table, values,  prioritys = 0):
        '''
        @summary: 使用有序set集合存储数据， 去重
        ---------
        @param table:
        @param values: 值； 支持list 或 单个值
        @param prioritys: 优先级； double类型，支持list 或 单个值。 根据此字段的值来排序, 值越大越优先。 可不传值，默认value的优先级为0
        ---------
        @result:若库中存在 返回0，否则入库，返回1。 批量添加返回None
        '''
        if isinstance(values, list):
            if not isinstance(prioritys, list):
                prioritys = [prioritys] * len(values)
            else:
                assert len(values) == len(prioritys), 'values值要与prioritys值一一对应'

            self._pipe.multi()
            for value, priority in zip(values, prioritys):
                self._pipe.zadd(table, value, -priority)
            self._pipe.execute()

        else:
            return self._redis.zadd(table, values, -prioritys)

    def zget(self, table, start_pos = 0, end_pos = 0, is_pop = True):
        '''
        @summary: 从有序set集合中获取数据
        ---------
        @param table:
        @param start_pos:开始位置(包含)
        @param end_pos:结束位置（包含）；如 0,1 则获取下标0到1的数据，下标为1的数据也返回
        @param is_pop:获取数据后，是否在原set集合中删除，默认是
        ---------
        @result:
        '''

        self._pipe.multi() # 标记事务的开始 参考 http://www.runoob.com/redis/redis-transactions.html
        self._pipe.zrange(table, start_pos, end_pos) # 取值
        if is_pop: self._pipe.zremrangebyrank(table, start_pos, end_pos) # 删除
        results, count = self._pipe.execute()
        return results

    def zget_cout(self, table):
        '''
        @summary: 获取表数据的数量
        ---------
        @param table:
        ---------
        @result:
        '''

        return self._redis.zcard(table)

    def lpush(self, table, values):
        if isinstance(values, list):
            self._pipe.multi()
            for value in values:
                self._pipe.rpush(table, value)
            self._pipe.execute()

        else:
            return self._redis.rpush(table, values)

    def lpop(self, table, count = 1):
        '''
        @summary:
        ---------
        @param table:
        @param count:
        ---------
        @result: 返回列表
        '''
        datas = []

        count = count if count <= self.lget_count(table) else self.lget_count(table)

        if count:
            if count > 1:
                self._pipe.multi()
                while count:
                    data = self._pipe.lpop(table)
                    count -= 1
                datas = self._pipe.execute()

            else:
                datas.append(self._redis.lpop(table))

        return datas

    def lget_count(self, table):
        return self._redis.llen(table)

    def clear(self, table):
        self._redis.delete(table)

if __name__ == '__main__':
    db = RedisDB()
    # data = {
    #     "url": "http://www.icm9.com/",
    #     "status": 0,
    #     "remark": {
    #         "spider_depth": 3,
    #         "website_name": "早间新闻",
    #         "website_position": 23,
    #         "website_domain": "icm9.com",
    #         "website_url": "http://www.icm9.com/"
    #     },
    #     "depth": 0,
    #     "_id": "5b15f33d53446530acf20539",
    #     "site_id": 1,
    #     "retry_times": 0
    # }
    # print(db.sadd('25:25', data))
    # print(db.zadd('26:26', [data]))
    # # print(db.sadd('1', 1))
    data = db.lpop('news:news_urls', 3)
    print(data)
    # print(type(data[0]))
    # db.clear('name')
    # import time
    # start = time.time()
    # # for i in range(10000):
    # #     db.zadd('test6', i)
    # db.zadd('test7', list(range(10000)), [1])
    # print(time.time() - start)

    # db.zadd('test3', '1', 5)
    # db.zadd('test3', '2', 6)
    # db.zadd('test3', '3', 4)

    # data = db.zget('test3', 0, 1)
    # print(data)
