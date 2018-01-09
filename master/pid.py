# -*- coding: utf-8 -*-
'''
Created on 2018-01-05 15:01
---------
@summary: 记录pid 在主函数中import pid即可
---------
@author: Boris
'''

import os

PID_PATH = './pid/'

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        pass

def write_file(filename, content, mode = 'w'):
    '''
    @summary: 写文件
    ---------
    @param filename: 文件名（有路径）
    @param content: 内容
    @param mode: 模式 w/w+ (覆盖/追加)
    ---------
    @result:
    '''

    directory = os.path.dirname(filename)
    mkdir(directory)
    with open(filename, mode, encoding = 'utf-8') as file:
        file.writelines(content)

def get_filepath_filename_fileext(file_path):
    '''
    @summary: 获取文件路径 名称 后缀
    ---------
    @param file_path: 文件的绝对路径
    ---------
    @result:
    '''
    file_path, file_name = os.path.split(file_path)
    shot_name, extension = os.path.splitext(file_name)
    return file_path, shot_name, extension


def get_pid():
    return os.getpid()

def record_pid(file_name):
    pid = get_pid()
    print('%s 进程pid为 %d '%(file_name, pid))

    pid_file_name = get_filepath_filename_fileext(file_name)[1]
    write_file(PID_PATH  + pid_file_name + '.txt', str(pid))
