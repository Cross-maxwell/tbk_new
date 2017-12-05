# coding=utf-8

import requests
import time
import threading
import os,sys

import logging
sys.path.append('/home/renyangfar/project/new_taobaoke/taobaoke/')

import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()
logger = logging.getLogger("utils")

from account.models.order_models import Order
from broadcast.models.user_models import TkUser
from django.contrib.auth.models import User

import basic


def pushNotice(order):
    for order_id in order:
        try:
            order = Order.objects.filter(order_id=order_id).first()
            order_head = '恭喜又有新订单啦。。。'
            order_id = order.order_id
            order_price = order.good_price
            order_time = order.create_time
            order_earn = order.show_commision_amount
            order_foot = '再接再厉哦！！！'
            user_id = int(order.user_id)
            # md_username = User.objects.filter(id=user_id).first().username
            openid = TkUser.objects.filter(user_id=user_id).first().openid
            if openid:
                send_msg = {
                    "touser": openid,
                    "template_id": basic.TEMPLATE_ID,
                    "url": basic.MMT_URL,
                    "data": {
                        "first": {
                            "value": order_head,
                            "color": "#173177"
                        },
                        "keyword1": {
                            "value": order_id,
                            "color": "#173177"
                        },
                        "keyword2": {
                            "value": order_price,
                            "color": "#173177"
                        },
                        "keyword3": {
                            "value": order_time,
                            "color": "#173177"
                        },
                        "keyword4": {
                            "value": order_earn,
                            "color": "#173177"
                        },
                        "remark": {
                            "value": order_foot,
                            "color": "#173177"
                        }
                    }
                }
                send(send_msg)
        except Exception as e:
            logger.error(e)


def send(send_msg):
    ACCESS_TOKEN = basic.Basic.accessToken
    send_url = 'https://api.weixin.qq.com/cgi-bin/message/' \
               'template/send?access_token=' + ACCESS_TOKEN
    res = requests.post(send_url, json=send_msg)
    print 'response state:', res.status_code


if __name__ == '__main__':
    # b = basic.Basic()
    # threading.Thread(target=b.run, name='baseLoop').start()
    # time.sleep(3)
    order = ['2680178799280122','5977258121980758']
    pushNotice(order)
