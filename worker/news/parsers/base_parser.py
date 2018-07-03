# -*- coding: utf-8 -*-
'''
Created on 2017-01-03 11:05
---------
@summary: 提供一些操作数据库公用的方法
---------
@author: Boris
'''
import sys
sys.path.append('../../')
import init

import utils.tools as tools
from db.elastic_search import ES
from base.article_manager import ArticleManager

es = ES()
article_manager = ArticleManager('news:news_article')
article_manager.start()


def add_news_acticle(uuid, title, author, release_time, website_name, website_domain, website_position, url, content):
    article = {
        'uuid' : uuid,
        'title' : title,
        'author' : author,
        'release_time' : release_time,
        'website' : website_name,
        'domain' : website_domain,
        'position' : website_position,
        'url' : url,
        'content' : content,
        'record_time' : tools.get_current_date()
    }

    # if not es.get('news_article', uuid):
    #     es.add('news_article', article, uuid)
    article_manager.put_articles(article)