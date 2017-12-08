# -*- coding: utf-8 -*-
'''
Created on 2017-06-30 16:34
---------
@summary: 环形队列,支持多线程
---------
@author: Boris
'''
import threading

class RingBuff():
    def __init__(self, size):
        self._lock = threading.RLock()

        self._max_size = size + 1
        self._buff = []
        self._read_pos = -1
        self._write_pos = -1

    def get_data(self, count):
        self._lock.acquire() #加锁
        urls = []

        count = count if count <= self.get_max_read_size() else self.get_max_read_size()
        end_pos = self._read_pos + count + 1
        if end_pos > self._max_size:
            urls.extend(self._buff[self._read_pos + 1:])
            urls.extend(self._buff[: end_pos % self._max_size])
        else:
            urls.extend(self._buff[self._read_pos + 1: end_pos])

        if urls:
            self._read_pos += len(urls)
            self._read_pos %= self._max_size

        self._lock.release()

        return urls


    def put_data(self, data):
        data = data if isinstance(data, list) else [data]
        if not data:
            return

        self._lock.acquire() #加锁

        data_count = len((data)) if len((data)) <= self.get_max_write_size() else self.get_max_write_size()
        if len(data) > data_count:
            print('环形队列已满，溢出：%s'%data[data_count:])

        # 添加url 到 _buff
        end_pos = data_count + self._write_pos + 1
        # 判断是否超出队列容量 超出的话超出的部分需要从头写
        # 超出部分
        overflow_end_pos = end_pos - self._max_size
        # 没超出部分
        in_pos =  end_pos if end_pos <= self._max_size else self._max_size

        # 没超出部分的数量
        data_cut_pos = in_pos - self._write_pos - 1



        self._buff[self._write_pos + 1 : in_pos] = data[:data_cut_pos]
        if overflow_end_pos > 0:
            self._buff[:overflow_end_pos] = data[data_cut_pos:]


        self._write_pos += data_count
        self._write_pos %= self._max_size   # -1 取余时问题  -1 % 1000

        self._lock.release()

    def get_max_write_size(self):
        size = 0
        if self._read_pos == self._write_pos:
            size = self._max_size
        elif self._read_pos < self._write_pos:
            size = self._max_size - (self._write_pos - self._read_pos)
        else:
            size = self._read_pos - self._write_pos

        return size - 1

    def get_max_read_size(self):
        return self._max_size -1 - self.get_max_write_size()

if __name__ == '__main__':
    a = RingBuff(5)
    a.put_data([1,2,3,4,5,6])
    data = a.get_data(5)
    print(data)
    a.put_data(3)
    data = a.get_data(5)
    print(data)
    data = a.get_data(5)
    print(data)
