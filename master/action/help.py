# -*- coding: utf-8 -*-
'''
Created on 2017-08-02 09:24
---------
@summary: 接口文档
---------
@author: Boris
'''
from markdown import markdown
import codecs
import web

render = web.template.render('templates')

class Help(object):
    """docstring for InterfaceDecument"""
    def GET(self, name):
        '''
        @summary: 帮助文档
        ---------
        @param name: url 地址映射后面的 正则表达式匹配到的结果。
        如URLS = (
            '/(.*)', 'service.help.Help'
        )
        name 为（.*）

        ---------
        @result:
        '''
        web.header('Content-Type','text/html;charset=UTF-8')
        readme = codecs.open("README.md", mode="r", encoding="utf8")
        decument = readme.read()
        readme.close()

        exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']

        return render.README(markdown(decument, extensions = exts)) #extensions 更改显示方式 参考http://pythonhosted.org/Markdown/extensions/
