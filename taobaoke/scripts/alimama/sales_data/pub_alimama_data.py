# -*- coding: utf-8 -*-
import os
import sys


sys.path.append('/home/new_taobaoke/taobaoke/')
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()
from datetime import datetime
import xlrd
reload(sys)
sys.setdefaultencoding('utf-8')

from account.models.order_models import Order
from account.utils.commision_utils import cal_commision, cal_agent_commision
from broadcast.models.entry_models import Product

send_msg_url = 'http://s-prod-04.qunzhu666.com:10024/api/robot/send_msg/'
send_msg_url2 = 'http://s-prod-04.qunzhu666.com:10024/api/robot/send_mmt_msg'

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
        # =================================== to be deleted on 2018.01.23
        # 12 月应失效已结算订单， 01.22结算完后删除此临时条件。
        tmp_orderlist = ['103464948244158964', '103994545408936737', '105064483564347613', '99319425000698282', '105933855709464234', '99431763401739791']
        tmp_orderlist += ['98188871442438090', '99938914993063108', '94398810214883174', '99930540669909042', '94404831691893574',
                          '98325817771190283', '98367370374190283', '94428236370806770', '100617716909456530', '100640873530937620',
                          '101053762266754347', '101244160771708429', '101712659983176303', '102152679748475635', '102041096048937620',
                          '102040452231937620', '102155254563105145', '102601514862875055', '102706908110580616', '103101179193069444',
                          '94793441614883174', '103197947794707131', '103224123193798862', '103420378060573812', '103326717625826035',
                          '103331561467826035', '94865820491372273', '103372581048826035', '103502474008826035', '103464948244158964',
                          '99051130258113587', '103559956211748346', '103606546231323456', '103599353352165935', '103940024494590160',
                          '103994545408936737', '104080309124558927', '95013102655372273', '104332507358573812', '94996468003470970',
                          '99151455937293890', '104728928755708429', '104753400846965026', '99315812967438090', '105064483564347613',
                          '99319425000698282', '99267683186438090', '105171160254185220', '105176364866343064', '99365989809152389',
                          '105341710026176303', '105316424700707131', '105370913211801421', '105614540865152107', '105920860931937620',
                          '106126215509483213', '99557396513257687', '99593294348668198', '106244823444470716', '95324322651002470',
                          '106225501205937620', '106625143311590160', '106694166900647144', '106708108706638427', '106813836213937620',
                          '106879582619418332', '99802874854515688', '99861086730097396', '107599682037590160', '107494741173026817',
                          '107715299846207347', '107750271518707131', '99844735040668198', '107813298273254850', '99920559757257687',
                          '107988406047590160', '100054818985040687', '108529119600937620', '108474519000247902', '108717444840937620',
                          '100143465213834581', '108847140455937620', '108912632884635039', '109272377598937620', '109493999824937620',
                          '110068223612914644', '95781476087755768', '110468959751222940', '111152409754563342', '111622809069937620',
                          '111665565257786212', '111999802048523303', '100913184337257687', '112362038306538115', '112526034470395820',
                          '101610302247257687', '101721826694863064', '102126342180468770', '102478162300468770',
                          '114932576142937620', '115014898373937620', '116420527496931214']
        tmp_condition = result_dict['order_id'] not in tmp_orderlist
        # 2017.12.13 王培钦：低于15%就算失效
        # 2018.12.18 对于付款状态的订单，也按照15%做失效判断
        create_time = datetime.strptime(result_dict['create_time'], "%Y-%m-%d %H:%M:%S")
        if result_dict['order_status'] == u'订单付款' and (create_time < datetime(2017,12,19)):
            pass
        else:
        # =================================== to be deleted on 2018.01.23
        # and unindent below block  --------------------    下面的if条件中， 最后一个判断时间的条件，到2018.01.23删除！
            if (float(result_dict['commision_rate'][:-2])/100.0 < 0.05) and tmp_condition and (not datetime(2017, 12, 19) < create_time < datetime(2017, 12, 27,06,25,00)) :
                result_dict['order_status'] = u'订单失效'
                result_dict['pay_amount'] = 0
                result_dict['show_commision_amount'] = 0.0

        try:
            result = Order.objects.update_or_create(order_id=result_dict['order_id'], defaults=result_dict)
            status = result[1]
            if status:
                insert_num += 1
                if u'失效' not in result_dict['order_status']:
                    new_order.append(result_dict['order_id'])
                    beary_chat('新增订单:{}'.format(result_dict['order_id']))
            elif not status:
                update_num += 1
        except Exception, e:
            print e
            continue
    leave_num = nrows - 1 - update_num - insert_num
    return_str = '\n{0}Exist Orders Updated, \n{1} New Orders Inserted  ,\n{2} Exceptions Raised .'.format(update_num, insert_num, leave_num)
    logger.info(return_str)

    cal_commision()
    cal_agent_commision()
    order_notice(new_order)
    pushNotice(new_order)

#
# def assert_low_rate(item_id):
#     # 判断是否低佣.
#     try:
#         p = Product.objects.get(item_id=item_id)
#         order = Order.objects.get(good_id=item_id)
#         p_rate = round(float(p.commision_amount)/p.price, 2)
#         order_rate = round(float(order.commision_amount)/order.pay_amount, 2)
#         if p_rate - order_rate > 0.15:
#             return True
#         else:
#             return False
#     except Product.DoesNotExist:
#         return False
#     except Exception, e:
#         print e.message
#         return False


def order_notice(order):
    user_list = []
    data = [u'[愉快]恭喜我们群里又有成员抢到高额优惠券啦～',]
    for order_id in order:
        try:
            order = Order.objects.filter(order_id=order_id).first()
            user_id = order.user_id
            md_username = User.objects.filter(id=int(user_id)).first().username
            user_list.append(md_username)
        except Exception as e:
            logger.error(e)
    for md_username in user_list:
        request_data = {
            "md_username": md_username,
            "data": data
        }

        notice_msg = '发送新订单通知到用户: {}'.format(md_username)
        beary_chat(notice_msg)
        logger.info(notice_msg)

        #send_msg_response = requests.post(send_msg_url, data=json.dumps(request_data))
        payload = {'md_username': md_username}
        send_msg_response2 = requests.get(send_msg_url2, params=payload)

        #logger.info("request wxbot status code: {}".format(send_msg_response.status_code))
        logger.info("request wxbot status code2: {}".format(send_msg_response2.status_code))



if __name__ == '__main__':
    push_data()


