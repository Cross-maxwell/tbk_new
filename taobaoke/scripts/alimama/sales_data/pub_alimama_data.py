# -*- coding: utf-8 -*-
import xlrd
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
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

file_path = 'scripts/alimama/pub_alimama_settle_excel.xls'
# file_name = 'pub_alimama_settle_excel.xls'
# file_path = os.path.join(os.path.abspath('.'), file_name)

print file_path


def push_data():
    data = xlrd.open_workbook(file_path)

    # 拿到第一张表
    table = data.sheets()[0]

    # 获取总行数
    nrows = table.nrows

    # 第一行是header
    headers = table.row_values(0)
    result_list = []
    result_dict = {}
    # print [result_dict for i in range(1, nrows) for j in range(len(headers))]

    # 二维遍历, 拼凑出json返回给接口
    for i in range(1, nrows):
        for j in range(len(headers)):
            if table.row_values(i)[j] is not None and table.row_values(i)[j] != "":
                # 映射后端需要的字段
                result_dict[field_mapping[headers[j]]] = table.row_values(i)[j]
        # print result_dict
        result_list.append(result_dict)
        result_dict = {}
    # 本地调试
    # request_result = requests.post('http://10.30.3.99:8000/api/tk/order-batch-create', json=result_list)
    # result_list = json.dumps(result_list)
    # batch接口
    request_result = requests.post('http://dianjin.shequn365.com/api/tk/order-batch-create', json=result_list)
    # result_dict = json.dumps(result_dict)
    # 单个接口
    # request_result = requests.post('http://dianjin.shequn365.com/api/tk/order-create', data=result_dict)
    print 'complete push data'
    print request_result.text


if __name__ == '__main__':
    push_data()
