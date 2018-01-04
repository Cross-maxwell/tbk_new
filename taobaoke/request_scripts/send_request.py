# -*- coding: utf-8 -*-


"""
    每隔45秒发送一次请求
"""
import os
rpath = os.path.abspath('../apps')
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})

import sys
sys.path.append(rpath)

import django
django.setup()

import time
import requests
from broadcast.views.taobaoke_views import global_push_from_fifo

time_format = "%Y-%m-%d %H:%M:%S"
headers = {"Connection": "close"}

# 路径 /home/new_taobaoke/taobaoke/request_scripts/send_request.py

while True:
    localtime = time.localtime(time.time())
    now_hour = int(time.strftime('%H', localtime))
    now_time = time.strftime(time_format, localtime)
    try:
        global_push_from_fifo()
        now_hour = int(time.strftime('%H', time.localtime(time.time())))
        if 7 <= now_hour <= 22:
            response = requests.get("http://s-prod-07.qunzhu666.com:9090/tk/push_product", headers=headers)
            print("{}: 请求/tk/push_product状态--{}".format(now_time, response.status_code))
        else:
            # 如果不在这个时间段 休眠长一点
            time.sleep(20 * 60)
    except Exception as e:
        print("{}: 请求/tk/push_product出现异常--{}".format(now_time, e))

    time.sleep(45)
