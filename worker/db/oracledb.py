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
import cx_Oracle
import utils.tools as tools
from utils.log import log
import datetime
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8' # 防止查出的中文乱码

STOP_ORCL = False #禁用oracle

IP        = tools.get_conf_value('config.conf', 'oracledb', 'ip')
PORT      = int(tools.get_conf_value('config.conf', 'oracledb', 'port'))
DB        = tools.get_conf_value('config.conf', 'oracledb', 'db')
USER_NAME = tools.get_conf_value('config.conf', 'oracledb', 'user_name')
USER_PASS = tools.get_conf_value('config.conf', 'oracledb', 'user_pass')

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls, *args, **kwargs)

        return cls._inst


class OracleDB(Singleton):
    def __init__(self, ip = IP, port = PORT, db = DB, user_name = USER_NAME, user_pass = USER_PASS):
        super(OracleDB, self).__init__()

        if STOP_ORCL:
            return

        if not hasattr(self,'conn'):
            try:
                print(user_name, user_pass, '%s:%d/%s'%(ip, port, db))
                self.conn = cx_Oracle.connect(user_name, user_pass, '%s:%d/%s'%(ip, port, db))#, threaded=True,events = True)
                self.cursor = self.conn.cursor()
            except Exception as e:
                raise
            else:
                log.debug('连接到数据库 %s'%db)

    def __cover_clob_to_str(self, datas):
        for i in range(len(datas)):
            temp_data = []
            for data in datas[i]:
                if isinstance(data, cx_Oracle.LOB) or isinstance(data, datetime.datetime):
                    data = str(data)
                temp_data.append(data)

            datas[i] = temp_data

        return datas


    def find(self, sql, fetch_one = False, to_json = False):
        if STOP_ORCL:
            return []

        result = []
        if fetch_one:
            result =  self.cursor.execute(sql).fetchone()
        else:
            # result =  self.cursor.execute(sql).fetchall()
            self.cursor.execute(sql)
            # 处理clob和date字段
            def fix_lob(row):
                def convert(col):
                    if isinstance(col, cx_Oracle.LOB) or isinstance(col, datetime.datetime):
                        return str(col)
                    else:
                        return col

                return [convert(c) for c in row]

            result =  [fix_lob(r) for r in self.cursor]

        if to_json:
            # result = self.__cover_clob_to_str(result)
            columns = [i[0] for i in self.cursor.description]
            # print(','.join(columns))
            result = [dict(zip(columns, r)) for r in result]

        return result

    def add(self, sql, exception_callfunc = ''):
        if STOP_ORCL:
            return True

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            if exception_callfunc:
                exception_callfunc(e)

            return False
        else:
            return True

    def update(self, sql):
        if STOP_ORCL:
            return True

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def delete(self, sql):
        if STOP_ORCL:
            return True

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def set_unique_key(self, table, key):
        if STOP_ORCL:
            return

        try:
            sql = 'alter table %s add unique (%s)'%(table, key)
            self.cursor.execute(sql)
            self.conn.commit()

        except Exception as e:
            log.error(table + ' ' + str(e) + ' key = '+ key)
        else:
            log.debug('%s表创建唯一索引成功 索引为 %s'%(table, key))

    def set_primary_key(self, table, key = "ID"):
        if STOP_ORCL:
            return

        try:
            sql = 'alter table {table_name} add constraint pk_{key} primary key ({key})'.format(table_name = table, key = key)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except Exception as e:
            log.error(table + ' ' + str(e) + ' key = '+ key)
        else:
            log.debug('%s表创建主键成功 主键为 %s'%(table, key))



    def close(self):
        if STOP_ORCL:
            return

        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    # 多线程测试
    # import threading

    db = OracleDB()
