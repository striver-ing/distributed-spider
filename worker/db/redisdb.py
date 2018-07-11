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
import utils.tools as tools
from utils.log import log

IP_PORTS   = tools.get_conf_value('config.conf', 'redis', 'ip_ports').split(',')
DB        = int(tools.get_conf_value('config.conf', 'redis', 'db'))
USER_PASS = tools.get_conf_value('config.conf', 'redis', 'user_pass')

if len(IP_PORTS) > 1:
    from rediscluster import StrictRedisCluster  # pip install redis-py-cluster
else:
    import redis

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls, *args, **kwargs)

        return cls._inst


class RedisDB():
    def __init__(self, ip_ports = IP_PORTS, db = DB, user_pass = USER_PASS):
        # super(RedisDB, self).__init__()

        if not hasattr(self,'_redis'):
            self._is_redis_cluster = False

            try:
                if len(ip_ports) > 1:
                    startup_nodes = []
                    for ip_port in ip_ports:
                        ip, port = ip_port.split(':')
                        startup_nodes.append({"host":ip, "port":port})

                    self._redis = StrictRedisCluster(startup_nodes=startup_nodes, decode_responses=True)
                    self._pipe = self._redis.pipeline(transaction=False)

                    self._is_redis_cluster = True

                else:
                    ip, port = ip_ports[0].split(':')
                    self._redis = redis.Redis(host = ip, port = port, db = db, password = user_pass, decode_responses=True) # redis默认端口是6379
                    self._pipe = self._redis.pipeline(transaction=True) # redis-py默认在执行每次请求都会创建（连接池申请连接）和断开（归还连接池）一次连接操作，如果想要在一次请求中指定多个命令，则可以使用pipline实现一次请求指定多个命令，并且默认情况下一次pipline 是原子性操作。

            except Exception as e:
                raise
            else:
                log.info('连接到redis数据库 %s'%(tools.dumps_json(ip_ports)))

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
            if not self._is_redis_cluster: self._pipe.multi()
            for value in values:
                self._pipe.sadd(table, value)
            self._pipe.execute()

        else:
            return self._redis.sadd(table, values)

    def sget(self, table, count = 0, is_pop = True):
        datas = []
        if is_pop:
            count = count if count <= self.sget_count(table) else self.sget_count(table)
            if count:
                if count > 1:
                    if not self._is_redis_cluster: self._pipe.multi()
                    while count:
                        self._pipe.spop(table)
                        count -= 1
                    datas = self._pipe.execute()

                else:
                    datas.append(self._redis.spop(table))

        else:
            datas =  self._redis.srandmember(table, count)

        return datas

    def sget_count(self, table):
        return self._redis.scard(table)

    def zadd(self, table, values,  prioritys = 0):
        '''
        @summary: 使用有序set集合存储数据， 去重(值存在更新)
        ---------
        @param table:
        @param values: 值； 支持list 或 单个值
        @param prioritys: 优先级； double类型，支持list 或 单个值。 根据此字段的值来排序, 值越小越优先。 可不传值，默认value的优先级为0
        ---------
        @result:若库中存在 返回0，否则入库，返回1。 批量添加返回None
        '''
        if isinstance(values, list):
            if not isinstance(prioritys, list):
                prioritys = [prioritys] * len(values)
            else:
                assert len(values) == len(prioritys), 'values值要与prioritys值一一对应'

            if not self._is_redis_cluster: self._pipe.multi()
            for value, priority in zip(values, prioritys):
                if self._is_redis_cluster:
                    self._pipe.zadd(table, priority, value)
                else:
                    self._pipe.zadd(table, value, priority)
            self._pipe.execute()

        else:
            if self._is_redis_cluster:
                return self._redis.zadd(table, prioritys, values)
            else:
                return self._redis.zadd(table, values, prioritys)

    def zget(self, table, count = 0, is_pop = True):
        '''
        @summary: 从有序set集合中获取数据
        ---------
        @param table:
        @param count: 数量
        @param is_pop:获取数据后，是否在原set集合中删除，默认是
        ---------
        @result: 列表
        '''
        start_pos = 0 # 包含
        end_pos = 0 if count == 0 else count - 1 # 包含

        if not self._is_redis_cluster: self._pipe.multi() # 标记事务的开始 参考 http://www.runoob.com/redis/redis-transactions.html
        self._pipe.zrange(table, start_pos, end_pos) # 取值
        if is_pop: self._pipe.zremrangebyrank(table, start_pos, end_pos) # 删除
        results, count = self._pipe.execute()
        return results

    def zget_count(self, table, priority_min = None, priority_max = None):
        '''
        @summary: 获取表数据的数量
        ---------
        @param table:
        @param priority_min:优先级范围 最小值（包含）
        @param priority_max:优先级范围 最大值（包含）
        ---------
        @result:
        '''

        if priority_min != None and priority_max != None:
            return self._redis.zcount(table, priority_min, priority_max)
        else:
            return self._redis.zcard(table)

    def lpush(self, table, values):
        if isinstance(values, list):
            if not self._is_redis_cluster: self._pipe.multi()
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
                if not self._is_redis_cluster: self._pipe.multi()
                while count:
                    data = self._pipe.lpop(table)
                    count -= 1
                datas = self._pipe.execute()

            else:
                datas.append(self._redis.lpop(table))

        return datas

    def lget_count(self, table):
        return self._redis.llen(table)

    def setbit(self, table, offset, value):
        self._redis.setbit(table, offset, value)

    def getbit(self, table, offset):
        return self._redis.getbit(table, offset)

    def clear(self, table):
        self._redis.delete(table)

if __name__ == '__main__':
    db = RedisDB()
    data = db.zget_count('news:worker_status', priority_min = 0, priority_max = 0)
    print(data)
