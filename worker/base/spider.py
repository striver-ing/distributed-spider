  # -*- coding: utf-8 -*-
'''
Created on 2017-01-09 10:38
---------
@summary: 组装parser、 parser_control 和 collector
---------
@author: Boris
'''

import sys
sys.path.append('../')
# from db.mongodb import MongoDB
import utils.tools as tools
from base.parser_control import PaserControl
from base.collector import Collector
import threading
from base.url_manager import UrlManager

class Spider(threading.Thread):
    def __init__(self, tab_urls, tab_site = '', tab_content  = '', parser_count = None, depth = None, parser_params = {}, begin_callback = None, end_callback = None, content_unique_key = 'url', delete_tab_urls = False, process_num = None):
        '''
        @summary:
        ---------
        @param tab_urls: url表名
        @param tab_site: 网站表名
        @param parser_count: parser 的线程数，为空时以配置文件为准
        @param parser_params : 解析器所用的參數
        @param begin_callback:  爬虫开始的回调
        @param end_callback:    爬虫结束的回调
        ---------
        @result:
        '''
        super(Spider, self).__init__()

        self._tab_urls = tab_urls
        self._url_manager = UrlManager(tab_urls)

        if delete_tab_urls:self._url_manager.clear_url()

        # self._db = MongoDB()
        # if delete_tab_urls: self._db.delete(tab_urls)

        # self._db.set_unique_key(tab_urls, 'url')
        # if tab_site: self._db.set_unique_key(tab_site, 'site_id')
        # if tab_content: self._db.set_unique_key(tab_content, content_unique_key)

        # #设置索引 加快查询速度
        # self._db.set_ensure_index(tab_urls, 'depth')
        # self._db.set_ensure_index(tab_urls, 'status')
        # if tab_site: self._db.set_ensure_index(tab_site, 'read_status')
        # if tab_content: self._db.set_ensure_index(tab_content, 'read_status')

        self._collector = Collector(tab_urls, depth, process_num)
        self._parsers = []

        self._parser_params = parser_params

        self._begin_callback = begin_callback
        # 扩展end_callback方法
        def _end_callback():
            # self._url_manager.stop()
            if end_callback: end_callback()

        self._end_callabck = _end_callback

        self._parser_count = int(tools.get_conf_value('config.conf', 'parser', 'parser_count')) if not parser_count else parser_count
        self._spider_site_name = tools.get_conf_value('config.conf', "spider_site", "spider_site_name").split(',')
        self._except_site_name = tools.get_conf_value('config.conf', "spider_site", "except_site_name").split(',')

    def add_parser(self, parser):
        if self._spider_site_name[0] == 'all':
            for except_site_name in self._except_site_name:
                if parser.NAME != except_site_name.strip():
                    self._parsers.append(parser)
        else:
            for spider_site_name in self._spider_site_name:
                if parser.NAME == spider_site_name.strip():
                    self._parsers.append(parser)

    def run(self):
        self.__start()

    def __start(self):
        if self._begin_callback:
            self._begin_callback()

        if not self._parsers:
            if self._end_callabck:
                self._end_callabck()
            return

        # 启动parser 的add site 和 add root
        #print(self._parser_params)
        for parser in self._parsers:
            # parser.add_site_info()
            parser.add_root_url(self._parser_params)

        # 启动collector
        self._collector.add_finished_callback(self._end_callabck)
        self._collector.start()

        # 启动parser control
        while self._parser_count:
            parser_control = PaserControl(self._collector, self._tab_urls)

            for parser in self._parsers:
                parser_control.add_parser(parser)

            parser_control.start()
            self._parser_count -= 1
