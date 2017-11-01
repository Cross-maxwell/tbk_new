# -*- coding: utf-8 -*-
"""
    卖出去的商品结算。
"""
import datetime
from fetch_excel import fetch_excel
from fetch_cookie import fetch_cookie_fromfile
import pub_alimama_data
import time
import os
from fetch_cookie import detect_cookie
from utils import beary_chat


def __main__():
    """
    :return: True for Success, False for Fail
    """
    now_time = datetime.datetime.now()
    yes_time = (now_time + datetime.timedelta(days=-7)).strftime('%Y-%m-%d')
    now_time = now_time.strftime('%Y-%m-%d')
    cookie_str = fetch_cookie_fromfile()

    # 创建订单接口
    url = 'http://pub.alimama.com/report/getTbkPaymentDetails.json?queryType=1' \
          '&payStatus=&DownloadID=DOWNLOAD_REPORT_INCOME_NEW&startTime={0}&endTime={1}'.format(yes_time, now_time)
    print(url)

    # 检测cookie是否有效
    if detect_cookie(cookie_str, url):
        print "cookie success"
        if fetch_excel(cookie_str, url):
            pub_alimama_data.push_data()

        # 结算接口
        url = 'http://pub.alimama.com/report/getTbkPaymentDetails.json?queryType=3' \
              '&payStatus=3&DownloadID=DOWNLOAD_REPORT_INCOME_NEW&startTime={0}&endTime={1}'.format(yes_time, now_time)
        print(url)
        if fetch_excel(cookie_str, url):
            pub_alimama_data.push_data()
        # beary_chat("销售数据更新啦！～", channel=u"淘宝客问题反馈")
        return True
    else:
        return False


if __name__ == "__main__":
    mtime_before = os.stat('/home/new_taobaoke/taobaoke/scripts/alimama/cookie.txt').st_mtime - 1
    cookie_effective = True
    N = 0
    while True:
        print('{} time runs'.format(N))
        # 文件已经被更改 或者 cookie上一次是有效的
        if mtime_before != os.stat('/home/new_taobaoke/taobaoke/scripts/alimama/cookie.txt').st_mtime or cookie_effective:
            mtime_before = os.stat('/home/new_taobaoke/taobaoke/scripts/alimama/cookie.txt').st_mtime
            cookie_effective = __main__()
        time.sleep(5 * 60)
        N = N + 1
