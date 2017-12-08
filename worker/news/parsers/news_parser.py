import sys
sys.path.append('../../')

import base.base_parser as base_parser
import news.parsers.base_parser as self_base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
from extractor.article_extractor import ArticleExtractor
# print(article_extractor.article_extractor)
# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '新闻正文提取'

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    pass

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    for task in parser_params:
        website_id = task[0]
        website_name = task[1]
        website_position = task[2]
        website_url = task[3]
        website_domain = task[4]

        base_parser.add_url('news_urls', SITE_ID, website_url, remark = {'website_name':website_name, 'website_position':website_position, 'website_url':website_url, 'website_domain':website_domain})

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    website_name = remark['website_name']
    website_position = remark['website_position']
    website_url = remark['website_url']
    website_domain =  remark['website_domain']

    html = tools.get_html(root_url)
    if not html:
        base_parser.update_url('news_urls', root_url, Constance.EXCEPTION)
        return

    # 近一步取待做url
    urls = tools.get_urls(html)
    for url in urls:
        url = tools.get_full_url(website_url, url)
        if website_domain in url:
            base_parser.add_url('news_urls', SITE_ID, url, depth + 1, remark = remark)

    # 解析网页
    content = title = release_time = author = ''
    article_extractor = ArticleExtractor(root_url, html)
    content = article_extractor.get_content()
    if content:
        title = article_extractor.get_title()
        release_time = article_extractor.get_release_time()
        author = article_extractor.get_author()
        uuid = tools.get_uuid(title, website_domain) if title != website_name else tools.get_uuid(root_url)

        log.debug('''
            uuid         %s
            title        %s
            author       %s
            release_time %s
            website_name %s
            domain       %s
            position     %s
            url          %s
            content      %s
            '''%(uuid, title, author, release_time, website_name, website_domain, website_position, root_url, content))

        if tools.is_have_chinese(title) or tools.is_have_english(title):
            # 入库
            self_base_parser.add_news_acticle(uuid, title, author, release_time, website_name, website_domain, website_position, root_url, content)

if __name__ == '__main__':
    url_info = {'status': 0, 'site_id': 1, 'depth': 0, 'remark': {'website_name': '新昌县人民政府门户网站', 'website_position': 11, 'website_domain': 'xcjx.gov.cn', 'website_url': 'http://xcjx.gov.cn'}, 'url': 'http://xcjx.gov.cn', 'retry_times': 0, '_id': '5a2a4ff75344652b58fb26cb'}
    url_info = {'_id': '5a2a56ae5344653eb0dfb1ee', 'remark': {'website_domain': 'e.gmw.cn', 'website_name': '鄞州区公共事务受理中心', 'website_url': 'http://e.gmw.cn/2017-12/04/content_26998661.htm', 'website_position': 11}, 'status': 0, 'retry_times': 0, 'site_id': 1, 'depth': 0, 'url': 'http://e.gmw.cn/2017-12/04/content_26998661.htm'}
    # url_info ={'status': 0, 'site_id': 1, 'url': 'http://www.hzkj.org/2.html', 'depth': 1, 'retry_times': 0, '_id': '5a2a66b9534465417cf16f33', 'remark': {'website_position': 11, 'website_domain': 'hzkj.org', 'website_url': 'http://www.hzkj.org', 'website_name': '杭州科技工作者服务中心'}}
    parser(url_info)