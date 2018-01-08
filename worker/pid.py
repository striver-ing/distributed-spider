# -*- coding: utf-8 -*-
'''
Created on 2018-01-05 15:01
---------
@summary: 记录pid 在主函数中import pid即可
---------
@author: Boris
'''

import os

print('进程pid为 %d'%os.getpid())
with open('pid.txt', 'w') as file:
    file.write(str(os.getpid()))
