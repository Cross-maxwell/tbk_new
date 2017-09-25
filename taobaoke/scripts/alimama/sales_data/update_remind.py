# _*_ coding:utf-8 _*_
from datetime import datetime
from time import sleep
import requests
from scripts.alimama.sales_data.utils import beary_chat

"""

每日定时提醒更新销售数据的脚本

"""
url = "http://s-prod-04.qunzhu666.com:8000/product/qrcode"

if __name__ == "__main__":
    now = datetime.now()
    exec_time = now
    while True:
        now = datetime.now()
        if now.day != exec_time.day and now.hour > 9 and now.minute > 30:
            r = requests.get(url)
            if r.status_code != 200:
                beary_chat("提醒执行失败！", user="fatphone777")
            else:
                exec_time = datetime.now()
        sleep(10 * 60)
