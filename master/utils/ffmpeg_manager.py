# -*- coding: utf-8 -*-
'''
Created on 2017-07-07 14:02
---------
@summary: 对ffmpeg封装,需要将ffmpeg.exe拷贝到Python安装目录下
---------
@author: Boris
'''
import os

def convert_file_format(input_file, output_file, delete_input_file = False):
    '''
    @summary: 转码，需要将ffmpeg.exe拷贝到Python安装目录下
    ---------
    @param input_file:
    @param output_file:
    ---------
    @result:
    '''
    is_success = True

    if not os.path.exists(output_file):
        is_exception = os.system('ffmpeg -i %s %s'%(input_file, output_file))
        is_success = not is_exception

    print('''
        ----- 转码 ------
        原文件  %s
        转成    %s
        成功？  %s
        '''%(input_file, output_file, is_success))

    if is_success and delete_input_file:
        os.remove(input_file)

    return is_success
