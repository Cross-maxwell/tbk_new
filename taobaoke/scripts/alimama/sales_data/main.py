# -*- coding: utf-8 -*-
"""
    卖出去的商品结算。
"""


import sys
sys.path.append('/home/new_taobaoke/taobaoke/')
import datetime
from fetch_excel import fetch_excel
from fetch_cookie import fetch_cookie_fromfile
import pub_alimama_data
import time
import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from fetch_cookie import detect_cookie, COOKIES_PATH
from fuli.oss_utils import beary_chat
import logging
logger = logging.getLogger('sales_data')



def __main__():
    """
    :return: True for Success, False for Fail
    """
    logger.info("===========开始更新销售数据===========")
    now_time = datetime.datetime.now()
    yes_time = (now_time + datetime.timedelta(days=-7)).strftime('%Y-%m-%d')
    now_time = now_time.strftime('%Y-%m-%d')
    cookie_str = fetch_cookie_fromfile()

    # 全部订单接口，按照订单创建时间筛选一周内的订单
    url = 'http://pub.alimama.com/report/getTbkPaymentDetails.json?queryType=1' \
          '&payStatus=&DownloadID=DOWNLOAD_REPORT_INCOME_NEW&startTime={0}&endTime={1}'.format(yes_time, now_time)
    # print(url)
    # 检测cookie是否有效
    if detect_cookie(cookie_str, url):
        if fetch_excel(cookie_str, url):
            pub_alimama_data.push_data()

        # 第三方推广订单，"第三方服务来源"的值为"权益推广"，"分成比率"远低于正常订单。
        url = 'http://pub.alimama.com/report/getTbkPaymentDetails.json?queryType=4' \
              '&payStatus=3&DownloadID=DOWNLOAD_REPORT_INCOME_NEW&startTime={0}&endTime={1}'.format(yes_time, now_time)
        # print(url)
        if fetch_excel(cookie_str, url):
            pub_alimama_data.push_data()

        # 已结算订单，按结算时间筛选一周内的订单。
        # （作为对上一条的补充，以避免出现付款状态持续一周以上时，再也无法拉取到的情况）
        url = 'http://pub.alimama.com/report/getTbkPaymentDetails.json?queryType=3' \
              '&payStatus=3&DownloadID=DOWNLOAD_REPORT_INCOME_NEW&startTime={0}&endTime={1}'.format(yes_time, now_time)
        # print(url)
        if fetch_excel(cookie_str, url):
            pub_alimama_data.push_data()

        logger.info("===========销售数据更新成功！===========")
        return True
    else:
        logger.warning("==[跪了]==销售数据用的cookie跪了啊！==[跪了]==")
        beary_chat("销售数据用的cookie跪了啊跪了啊跪了啊！")
        return False


if __name__ == "__main__":
    mtime_before = os.stat(COOKIES_PATH).st_mtime - 1
    cookie_effective = True
    N = 0
    while True:
        print('{} time runs'.format(N))
        # 文件已经被更改 或者 cookie上一次是有效的
        if mtime_before != os.stat(COOKIES_PATH).st_mtime or cookie_effective:
            mtime_before = os.stat(COOKIES_PATH).st_mtime
            cookie_effective = __main__()
        time.sleep(5 * 60)
        N = N + 1
