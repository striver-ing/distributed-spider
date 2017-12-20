import sys
sys.path.append('../')
import init
import utils.tools as tools
from utils.log import log
from base.spider import Spider
from utils.export_data import ExportData

# 需配置
import news.task_status as task_status
from news.parsers import *

MASTER_ADDRESS = tools.get_conf_value('config.conf', 'master', 'address')
SEARCH_TASK_SLEEP_TIME = int(tools.get_conf_value('config.conf', 'task', 'search_task_sleep_time'))
def main():
    while True:
        if task_status.is_doing:
            tools.delay_time(SEARCH_TASK_SLEEP_TIME)
            continue

        task_status.is_doing = True

        # 查找任务
        get_task_url = MASTER_ADDRESS + '/task/get_task'
        print(get_task_url)
        update_task_url = MASTER_ADDRESS + '/task/update_task'
        tasks = tools.get_json_by_requests(get_task_url)
        print(tasks)

        def begin_callback():
            log.info('\n********** news begin **********')
            # 更新任务状态 doing

            data = {
                'tasks':str(tasks),
                'status':602
            }

            if tools.get_json_by_requests(update_task_url, data = data):
                log.debug('更新任务状态 正在做...')

        def end_callback():
            log.info('\n********** news end **********')
            task_status.is_doing = False

            data = {
                'tasks':str(tasks),
                'status':603
            }

            if tools.get_json_by_requests(update_task_url, data = data):
                log.debug('更新任务状态 已做完！')

        # 配置spider
        spider = Spider(tab_urls = 'news_urls', begin_callback = begin_callback, end_callback = end_callback, parser_params = tasks, delete_tab_urls = True)

        # 添加parser
        spider.add_parser(news_parser)

        spider.start()

if __name__ == '__main__':
    main()