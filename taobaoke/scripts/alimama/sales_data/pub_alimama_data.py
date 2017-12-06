# -*- coding: utf-8 -*-
import os
import sys


sys.path.append('/home/new_taobaoke/taobaoke/')
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

import xlrd
reload(sys)
sys.setdefaultencoding('utf-8')

from account.models.order_models import Order
from account.utils.commision_utils import cal_commision, cal_agent_commision
from broadcast.models.entry_models import Product

send_msg_url = 'http://s-prod-04.qunzhu666.com:10024/api/robot/send_msg/'

import requests
from django.contrib.auth.models import User
import json
from fuli.oss_utils import beary_chat
from scripts.wx_gzh.gzh_service import pushNotice

import logging
logger = logging.getLogger("utils")


field_mapping = {u'创建时间': 'create_time',
                 u'点击时间': 'click_time',
                 u'商品信息': 'good_info',
                 u'商品ID': 'good_id',
                 u'掌柜旺旺': 'wangwang',
                 u'所属店铺': 'shop',
                 u'商品数': 'good_num',
                 u'商品单价': 'good_price',
                 u'订单状态': 'order_status',
                 u'订单类型': 'order_type',
                 u'收入比率': 'earning_rate',
                 u'分成比率': 'share_rate',
                 u'付款金额': 'pay_amount',
                 u'效果预估': 'result_predict',
                 u'结算金额': 'balance_amount',
                 u'预估收入': 'money_amount',
                 u'结算时间': 'earning_time',
                 u'佣金比率': 'commision_rate',
                 u'佣金金额': 'commision_amount',
                 u'补贴比率': 'subsidy_rate',
                 u'补贴金额': 'subsidy_amount',
                 u'补贴类型': 'subsidy_type',
                 u'成交平台': 'terminalType',
                 u'第三方服务来源': 'third_service',
                 u'订单编号': 'order_id',
                 u'类目名称': 'category_name',
                 u'来源媒体ID': 'source_id',
                 u'来源媒体名称': 'source_media',
                 u'广告位ID': 'ad_id',
                 u'广告位名称': 'ad_name'}

## merge时处理一下

file_path = 'scripts/alimama/pub_alimama_settle_excel.xls'
#file_name = 'pub_alimama_settle_excel.xls'
#file_path = os.path.join(os.path.abspath('..'), file_name)


def push_data():
    data = xlrd.open_workbook(file_path)
    # 拿到第一张表
    table = data.sheets()[0]
    # 获取总行数
    nrows = table.nrows
    # 第一行是header
    headers = table.row_values(0)
    result_dict = {}
    # 二维遍历, 拼凑出dict用于存库
    update_num = 0
    insert_num = 0
    new_order = []
    for i in range(1, nrows):
        for j in range(len(headers)):
            if table.row_values(i)[j] is not None and table.row_values(i)[j] != "":
                # 映射后端需要的字段
                result_dict[field_mapping[headers[j]]] = table.row_values(i)[j]
        # item_id = result_dict['good_id']
        if float(result_dict['commision_rate'][:-2])<0.2 and result_dict['order_status']==u'订单结算':
            result_dict['order_status'] = u'订单失效'
            result_dict['pay_amount'] = 0
            result_dict['show_commision_amount']=0.0
        try:
            result = Order.objects.update_or_create(order_id=result_dict['order_id'], defaults=result_dict)
            status = result[1]
            if status:
                insert_num += 1
                new_order.append(result_dict['order_id'])
                beary_chat('新增订单:{}'.format(result_dict['order_id']))
            elif not status:
                update_num += 1
        except Exception, e:
            print e
            continue
    leave_num = nrows - 1 - update_num - insert_num
    return_str = '更新 {0} 条已存在订单数据，\n插入 {1} 条新订单数据,\n有 {2} 条数据出错.'.format(update_num, insert_num, leave_num)
    logger.info(return_str)

    cal_commision()
    cal_agent_commision()
    order_notice(new_order)
    pushNotice(new_order)

# 改规则了，不用了
# def assert_low_rate(item_id):
#     # 判断是否低佣.
#     try:
#         p = Product.objects.get(item_id=item_id)
#         order = Order.objects.get(good_id=item_id)
#         p_rate = round(float(p.commision_amount)/p.price, 2)
#         order_rate = round(float(order.commision_amount)/order.pay_amount, 2)
#         if p_rate - order_rate > 0.1:
#             return True
#         else:
#             return False
#     except Product.DoesNotExist:
#         return False
#     except Exception, e:
#         print e.message
#         return False


def order_notice(order):
    user_set = set()
    data = [u'有新订单啦，请查收。',]
    for order_id in order:
        try:
            order = Order.objects.filter(order_id=order_id).first()
            user_id = order.user_id
            md_username = User.objects.filter(id=int(user_id)).first().username
            user_set.add(md_username)
        except Exception as e:
            logger.error(e)
    for md_username in user_set:
        request_data = {
            "md_username": md_username,
            "data": data
        }

        notice_msg = '发送新订单通知到用户: {}'.format(md_username)
        beary_chat(notice_msg)
        logger.info(notice_msg)

        send_msg_response = requests.post(send_msg_url, data=json.dumps(request_data))
        logger.info("request wxbot status code: {}".format(send_msg_response.status_code))



if __name__ == '__main__':
    push_data()


