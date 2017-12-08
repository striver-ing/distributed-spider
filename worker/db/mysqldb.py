 # -*- coding: utf-8 -*-
'''
Created on 2016-11-16 16:25
---------
@summary: 操作oracle数据库
---------
@author: Boris
'''
import sys
sys.path.append('../')
import init
import pymysql
import utils.tools as tools
from utils.log import log

IP        = tools.get_conf_value('config.conf', 'mysql', 'ip')
PORT      = int(tools.get_conf_value('config.conf', 'mysql', 'port'))
DB        = tools.get_conf_value('config.conf', 'mysql', 'db')
USER_NAME = tools.get_conf_value('config.conf', 'mysql', 'user_name')
USER_PASS = tools.get_conf_value('config.conf', 'mysql', 'user_pass')

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls, *args, **kwargs)

        return cls._inst


class MysqlDB(Singleton):
    def __init__(self, ip = IP, port = PORT, db = DB, user_name = USER_NAME, user_pass = USER_PASS):
        super(MySQL, self).__init__()

        if not hasattr(self,'conn'):
            try:
                self.conn = pymysql.connect(host = ip, port = port, user = user_name, passwd = user_pass, db = db, charset = 'utf8')
                self.cursor = self.conn.cursor()
            except Exception as e:
                raise
            else:
                log.debug('连接到数据库 %s'%db)

    def find(self, sql, fetch_one = False):
        result = []
        if fetch_one:
            result =  self.cursor.execute(sql).fetchone()
        else:
            result =  self.cursor.execute(sql).fetchall()

        return result

    def add(self, sql, exception_callfunc = ''):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            # log.error(e)
            if exception_callfunc:
                exception_callfunc(e)

            return False
        else:
            return True

    def update(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def set_unique_key(self, table, key):
        try:
            sql = 'alter table %s add unique (%s)'%(table, key)
            self.cursor.execute(sql)
            self.conn.commit()

        except Exception as e:
            log.error(table + ' ' + str(e) + ' key = '+ key)
        else:
            log.debug('%s表创建唯一索引成功 索引为 %s'%(table, key))

    def close(self):
        self.cursor.close()
        self.conn.close()