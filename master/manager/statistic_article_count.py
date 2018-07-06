# -*- coding: utf-8 -*-
'''
Created on 2018-07-06 15:31
---------
@summary: 舆情新闻信息统计
---------
@author: Boris
'''
import sys
sys.path.append('..')
import init
import utils.tools as tools

def get_article_count_msg(begin_time, end_time):

    # 查询爬取到的文章数量
    data_pool_address = 'http://192.168.60.16:9200/_sql?sql='
    sql = "SELECT count(*) FROM news_article where record_time >= '{begin_time}' and record_time <= '{end_time}'".format(begin_time = begin_time, end_time = end_time)
    data = tools.get_json_by_requests(data_pool_address + sql)
    total_article_count = data.get('aggregations').get('COUNT(*)').get('value')

    # 查询爬取到的新发布的文章数量
    data_pool_address = 'http://192.168.60.16:9200/_sql?sql='
    sql = "SELECT count(*) FROM news_article where release_time >= '{begin_time}' and release_time <= '{end_time}'".format(begin_time = begin_time, end_time = end_time)
    data = tools.get_json_by_requests(data_pool_address + sql)
    new_article_count = data.get('aggregations').get('COUNT(*)').get('value')

    # 查询入业务库的文章数量
    iopm_db_address = 'http://192.168.60.27:9200/_sql?sql='
    sql = "SELECT count(*) FROM tab_iopm_article_info where  INFO_TYPE = 1 and RECORD_TIME >= '{begin_time}' and RECORD_TIME <= '{end_time}'".format(begin_time = begin_time, end_time = end_time)
    data = tools.get_json_by_requests(iopm_db_address + sql)
    iopm_total_article_count = data.get('aggregations').get('COUNT(*)').get('value')

    # 查询入业务库的新发布的文章数量
    iopm_db_address = 'http://192.168.60.27:9200/_sql?sql='
    sql = "SELECT count(*) FROM tab_iopm_article_info where INFO_TYPE = 1 and RELEASE_TIME >= '{begin_time}' and RELEASE_TIME <= '{end_time}'".format(begin_time = begin_time, end_time = end_time)
    data = tools.get_json_by_requests(iopm_db_address + sql)
    iopm_new_article_count = data.get('aggregations').get('COUNT(*)').get('value')

    article_count_msg = '''
        \r共抓取到有效文章数量：%s
        \r共抓取到新发布文章数量：%s
        \r去重后入业务库文章总量: %s
        \r去重后入业务库新发布的文章数量：%s
    '''%(total_article_count, new_article_count, iopm_total_article_count, iopm_new_article_count)

    return article_count_msg

if __name__ == '__main__':
    begin_time = '2018-07-06 13:47:38'
    end_time = '2018-07-06 15:29:39'
    article_count_msg = get_article_count_msg(begin_time, end_time)
    print('''
        \r文章数量信息 %s
        '''%article_count_msg)