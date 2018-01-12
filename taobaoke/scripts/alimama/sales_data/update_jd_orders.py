# -*- coding: utf-8 -*-
"""
使用好京客接口查询订单
官网文档：http://jd.91fyt.com/index.php/index/api
"""
import os
import sys
import requests
from datetime import datetime, timedelta
import time

sys.path.append('/home/new_taobaoke/taobaoke/')
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from django.contrib.auth.models import User
from account.models.order_models import Order
from fuli.top_settings import hjk_apikey
import logging
logger = logging.getLogger('sales_data')

def update_jd_orders():
    begintime = int(time.mktime((datetime.now()-timedelta(days=15)).timetuple()))
    endtime = int(time.mktime(datetime.now().timetuple()))

    # 待结算订单接口
    url_1 = 'http://www.haojingke.com/index.php/api/index/myapi?' \
          'type=importorder&' \
          'apikey={apikey}&' \
          'begintime={begintime}&' \
          'endtime={endtime}'.format(
        apikey=hjk_apikey,
        begintime=begintime,
        endtime=endtime
    )

    # 已结算订单接口
    url_2 = 'http://www.haojingke.com/index.php/api/index/myapi?' \
          'type=importorder&' \
          'apikey={apikey}&' \
          'begintime={begintime}&' \
          'endtime={endtime}'.format(
        apikey=hjk_apikey,
        begintime=begintime,
        endtime=endtime
    )

    unliquidated_orders = requests.get(url_1, headers={'Connection':'close'}).json()['data']
    for o in unliquidated_orders:
        deal_with_order(o)
    liquidated_orders = requests.get(url_2, headers={'Connection':'close'}).json()['data']
    for o in liquidated_orders:
        deal_with_order(o)


def deal_with_order(order):
    o = order
    obj_dict={
        'create_time': datetime.fromtimestamp(int(o['orderTime'])),
        'order_type': '京东',
        'good_price': o['totalMoney'],
        'ad_id': o['positionId'],
    }
    try:
        user_id = User.objects.get(tkuser__jdadzone__pid=obj_dict['ad_id']).id
    except User.DoesNotExist:
        logger.warning('Updating JD Orders: User Query Does Not Exist. Ad_id : {}'.format(obj_dict['ad_id']))
        user_id = 'NotFound'
    obj_dict.update({'user_id': user_id})
    if float(o['commission']) == 0 or int(o['yn']) == 0:
        obj_dict.update({'order_status': u'订单失效'})
    elif int(o['finishTime']) != 0:
        obj_dict.update({'order_status': u'订单结算', 'earning_time': datetime.fromtimestamp(int(o['finishTime']))})
    else :
        obj_dict.update({'order_status': u'订单付款'})
    # 因京东一个订单下可能有多个商品，故对每个商品，按照 订单id+商品id作为唯一标识
    for i in get_good_list(o):
        try:
            obj_dict.update({'order_id': o['orderId'] + '-' + i['good_id']})
            obj_dict.update(i)
            Order.objects.update_or_create(order_id=obj_dict['order_id'], defaults=obj_dict)
            logger.info('Updated JD Order {}.'.format(obj_dict['order_id']))
        except Exception, e:
            logger.error('Error Occured When Updating JD Order {}.'.format(obj_dict['order_id']))
            logger.error(e)


def get_good_list(orders):
    ps_list = []
    ps = orders['skus']
    for p in ps:
        if float(p['cosPrice']) > 0:
            p_dict = {
                'good_info': p['skuName'],
                'good_id': p['skuId'],
                'good_num': int(p['skuNum'])-int(p['skuReturnNum']),
                'pay_amount': float(p['cosPrice']),
                'earning_rate': p['commissionRate'],
                'share_rate': p['subSideRate'],
                'commision_rate': 0 if float(p['cosPrice'])==0 else str(round((100*float(p['commission'])/float(p['cosPrice'])),2)) + ' %',
                'commision_amount': float(p['commission']),
            }
            ps_list.append(p_dict)
    return ps_list


if __name__=="__main__":
    update_jd_orders()