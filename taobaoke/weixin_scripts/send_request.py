# -*- coding: utf-8 -*-


"""
    每隔60秒发送一次请求
"""
import time
import requests

import logging
logger = logging.getLogger('post_taobaoke')

# 路径 /home/new_taobaoke/taobaoke/weixin_scripts/send_request.py

while True:
    try:
        now_hour = int(time.strftime('%H', time.localtime(time.time())))
        if 7 <= now_hour <= 22:
            requests.get("http://s-prod-04.qunzhu666.com:8080/push_product")
        else:
            # 如果不在这个时间段 休眠长一点
            time.sleep(20 * 60)
    except Exception as e:
        logging.error(e)
        print(e)

    time.sleep(60)