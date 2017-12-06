# coding=utf-8

import requests
import datetime
import os,sys

sys.path.append('/home/new_taobaoke/taobaoke/')
# sys.path.append('/root/project/new_taobaoke/taobaoke')

import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from django.core.cache import cache
import logging
logger = logging.getLogger("utils")

from account.models.order_models import Order
from broadcast.models.user_models import TkUser

import basic

GZH_ACESS_KEY = 'gzh_acess_key'

def pushNotice(order):
    for order_id in order:
        try:
            order = Order.objects.filter(order_id=order_id).first()
            order_head = '恭喜您又有新订单啦~'
            order_id = order.order_id
            order_price = str(round(order.pay_amount,2))
            create_time = order.create_time + datetime.timedelta(hours=8)
            outtime = create_time.strftime('%Y-%m-%d %H:%M:%S')
            order_time = str(outtime)
            order_earn = str(round(order.show_commision_amount,2))
            order_foot = '请再接再厉哦！'
            user_id = int(order.user_id)
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
    # ACCESS_TOKEN = basic.Basic.accessToken
    ACCESS_TOKEN = cache.get(GZH_ACESS_KEY)
    send_url = 'https://api.weixin.qq.com/cgi-bin/message/' \
               'template/send?access_token=' + ACCESS_TOKEN
    print 'ACCESS_TOKEN:'+ACCESS_TOKEN
    print send_msg
    res = requests.post(send_url, json=send_msg)
    print 'response state:', res.status_code


if __name__ == '__main__':
    # b = basic.Basic()
    # threading.Thread(target=b.run, name='baseLoop').start()
    # time.sleep(3)
    order = ['2680178799280122','5977258121980758']
    pushNotice(order)