# coding=utf-8

"""
    从www.lanlanlife.com的商品库中取出商品， 存入数据表 broadcast_product
"""
import sys
sys.path.append('/home/new_taobaoke/taobaoke')
import time
# sys.path.append('/home/smartkeyerror/PycharmProjects/new_taobaoke/taobaoke')
# print(sys.path)

import requests
import re
from fuli.oss_utils import beary_chat
import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from broadcast.models.entry_models import Product
from django.db import connection

import logging
logger = logging.getLogger('fetch_lanlan')

# f = open('/home/new_taobaoke/taobaoke/scripts/goods/lanlan_cookie.txt')

# 本地测试
f = open('lanlan_cookie.txt')
cookie_str = f.read()
f.close()


def main():
    for i in range(60):
        resp = requests.get(
            # 已发送
            'http://www.lanlanlife.com/taoke/sendlist/fetchList?uuid=803cef07c9c80627cd75d1bf8c97683a&type=1&page=%d' % (i+1),
            # 待发送
            #'http://www.lanlanlife.com/taoke/sendlist/gatherList?uuid=803cef07c9c80627cd75d1bf8c97683a&page=%d' % (i+1),
            headers={'Cookie': cookie_str.strip()}
        )
        if resp.json()['status']['code'] == 1001:
            try:
                for item in resp.json()['result']['items']:
                    if item['status'] != '1':
                        continue
                    data_dict = {
                        'title': item['itemTitle'],
                        'desc': item['recommend'],
                        'img_url': item['coverImage'].split('@')[0] + '?x-oss-process=image/resize,w_600/format,jpg/quality,Q_80',
                        'cupon_value': item['amount'],
                        'price': item['price'][1:],
                        'cupon_url': item['link'],
                        'sold_qty': item['monthSales'],
                        'cupon_left': item['surplus'],
                        'is_finished': item['isFinished'],
                        'commision_rate': item['tkRate'],
                        'commision_amount': float(item['tkPrice'].strip(u'\xa5'))
                    }

                    key_list = [
                        'title', 'desc', 'img_url',
                        'cupon_value', 'price', 'cupon_url',
                        'sold_qty', 'cupon_left', 'commision_rate', 'commision_amount',
                    ]
                    item_id = re.search('itemId=(\d+)', data_dict['cupon_url']).groups()[0]

                    if Product.objects.filter(item_id=item_id).exists():
                        p = Product.objects.get(item_id=item_id)
                        for key in key_list:
                            setattr(p, key, data_dict[key])
                        if data_dict['is_finished'] == 'true' or data_dict['cupon_left'] == 0:
                            p.available = False
                        else:
                            p.available = True
                        p.save()
                        logger.info('Product updated')
                    else:
                        p = Product.objects.create(**{key: data_dict[key] for key in key_list})

                    p.refresh_from_db()
                    p.assert_available()

                    connection.close()

            except Exception as e:
                logger.error(e)
                beary_chat("懒懒cookie已失效，请更新")
                print Exception.message
        else:
            # beary_chat('懒懒返回错误，msg : {}'.format(resp.json()['status']['msg']))
            logger.error('懒懒返回错误，msg : {}'.format(resp.json()['status']['msg']))

if __name__ == "__main__":
    while True:
        main()
        time.sleep(60 * 5)
