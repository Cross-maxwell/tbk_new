# coding=utf-8

"""
    从www.lanlanlife.com的商品库中取出商品， 存入数据表 broadcast_product
"""
import sys
sys.path.append('/home/new_taobaoke/taobaoke')
import time
import requests
import json
import re
from fuli.oss_utils import beary_chat
import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from broadcast.models.entry_models import Product, ProductDetail
from django.db import connection
from datetime import datetime
from fuli.top_settings import lanlan_apikey

import logging
logger = logging.getLogger('fetch_lanlan')


def main():
    start_time = datetime.now()
    logger.info('Start Fetch Lanlan at : {0} : {1} : {2} '.format(start_time.hour, start_time.minute, start_time.second))
    update_products()
    passed_time = datetime.now()-start_time
    logger.info('Totally Spent Time: {} Seconds.'.format(passed_time.total_seconds()))


def update_products():
    # 懒懒接口最多返回5000条， 此处每5分钟更新1000条
    for i in range(50):
        resp = requests.get(
            # 已发送
            'http://www.lanlanlife.com/product/itemList?apiKey={0}&sort=1&pageSize=20&page={1}'.format(lanlan_apikey,
                                                                                                       i),
            headers={'Connection': 'close'}
        )
        # 正常状态code为1001
        if resp.json()['status']['code'] == 1001:
            try:
                for item in resp.json()['result']:
                    product_dict = {
                        'title': item['shortTitle'],
                        'desc': '',
                        'img_url': item['coverImage'].split('@')[
                                       0] + '?x-oss-process=image/resize,w_600/format,jpg/quality,Q_80',
                        'cupon_value': float(item['couponMoney'].strip()),
                        'price': float(item['nowPrice'].strip()),
                        'cupon_url': item['couponUrl'],
                        'sold_qty': int(item['monthSales']),
                        'cupon_left': item['couponRemainCount'],
                        'commision_rate': str(item['tkRates']) + '%',
                        'commision_amount': item['tkRates'] * float(item['nowPrice'])/100,
                        'cate': item['category']
                    }
                    try:
                        send_img = item['sendImage']
                        img_size_str = re.findall('\_(\d+x\d+)\.', send_img)[0]
                        img_size = img_size_str.split('x')
                        img_scale = float(img_size[0])/float(img_size[1])
                        # 按照尺寸判断，尺寸在此范围内的认定为是直播秀的图，存库并发送用。
                        if 100.0/80 < img_scale < 100.0/60:
                            product_dict.update({'send_img': send_img})
                    except:
                        pass

                    item_id = item['itemId']
                    if item['tkRates'] >= 20:
                        p, created = Product.objects.update_or_create(item_id=item_id, defaults=product_dict)
                    else:
                        continue
                    if not datetime.fromtimestamp(
                            float(item['couponStartTime'])) < datetime.now() < datetime.fromtimestamp(
                        float(item['couponEndTime'])):
                        p.available = False
                    p.refresh_from_db()
                    p.assert_available()
                    update_productdetails(p, item)
                    logger.info('Product Updated!')
                    connection.close()
            except Exception as e:
                logger.error(e)
        else:
            logger.error('懒懒返回错误，msg : {}'.format(resp.json()['status']['msg']))


def update_productdetails(p_object, item):
    detail_dict = {}
    detail_dict['product'] = p_object
    detail_dict['seller_id'] = item['sellerId']
    detail_dict['seller_nick'] = item['sellerName']
    for i in range(len(item['auctionImages'])):
        if item['auctionImages'][i] and not item['auctionImages'][i].startswith('http'):
            item['auctionImages'][i] = 'http:' + item['auctionImages'][i]
    detail_dict['small_imgs'] = json.dumps(item['auctionImages'])
    for i in range(len(item['detailImages'])):
        if item['detailImages'][i] and not item['detailImages'][i].startswith('http'):
            item['detailImages'][i] = 'http:' + item['detailImages'][i]
    detail_dict['describe_imgs'] = json.dumps(item['detailImages'])
    detail_dict['recommend'] = item['recommend']
    ProductDetail.objects.update_or_create(product=p_object, defaults=detail_dict)
    connection.close()


if __name__ == "__main__":
    while True:
        main()
        time.sleep(60 * 5)
