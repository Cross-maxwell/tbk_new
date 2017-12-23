# -*- coding: utf-8 -*-
import re
import random
import json
import requests
import hashlib
import datetime
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache


from mini_program.settings import AppID, AppSecret, MCH_ID, IP, notify_url, prepay_url
from mini_program.utils import get_sign_str, get_random_str, get_trade_num
from mini_program.utils import trans_dict_to_xml, trans_xml_to_dict, beary_chat
from broadcast.models.entry_models import Product
from mini_program.models.payment_models import Payment, AppUser, UserAddress, AppSession

from user_auth.utils.stringUtil import random_num
from user_auth.utils.sendMessageUtil import send_message

import logging
logger = logging.getLogger("django_views")


# Todo: 用户登录状态如何维持？
"""
首先，排除Django-middleware，因为middleware会对全局的请求进行加工处理，而这里只是单独的一个session维护
1. 前端从何处传递session_key? headers, body, queryString?
    body，传递一个dict对象，多一个session_key字段即可
2. 后端session表组成:
    




"""

class PrepayView(View):
    def post(self, request):
        req_dict = json.loads(request.body)

        openid = req_dict["openid"]
        goods_id = req_dict["goods_id"]
        item_id = req_dict["item_id"]
        # 商品数量
        goods_num = req_dict["goods_num"]
        # 商品名称
        goods_title = req_dict["goods_title"]

        # 订单总金额，单位为分，详见支付金额
        try:
            product = Product.objects.get(item_id=item_id, id=goods_id)
            total_fee = int((product.price * int(goods_num)) * 100)
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({"ret": 0, "data": "商品不存在"}, status=404))

        body = goods_title
        if len(body) > 128:
            body = body[:128]

        attach = "商品附加数据测试"
        nonce_str = get_random_str()
        out_trade_no = get_trade_num(item_id=item_id)

        param_data = {
            "appid": AppID,
            # 附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
            # 微信支付分配的商户号
            "mch_id": MCH_ID,
            # 随机字符串，不长于32位。推荐随机数生成算法
            "nonce_str": nonce_str,
            "body": body,
            # 商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号,必须唯一
            "out_trade_no": out_trade_no,
            "total_fee": total_fee,
            # APP和网页支付提交用户端ip，Native支付填调用微信支付API的机器IP。
            "spbill_create_ip": IP,
            # 接收微信支付异步通知回调地址，通知url必须为直接可访问的url，不能携带参数。
            "notify_url": notify_url,
            "attach": attach,
            # 商品简单描述，该字段须严格按照规范传递，具体请见参数规定， 最长128位， 即最长40个中文
            "trade_type": "JSAPI",
            # 签名，详见签名生成算法
            "openid": openid
        }
        sorted_dict = sorted(param_data.iteritems(), key=lambda x: x[0])
        sign = get_sign_str(sorted_dict)
        param_data["sign"] = sign

        # 这里写XML是真的蠢，什么年代了还用这种鬼东西
        req_xml_data = trans_dict_to_xml(param_data)
        print req_xml_data

        try:
            response = requests.post(prepay_url, data=req_xml_data, headers={'Content-Type': 'text/xml'})
            logger.info("统一下单接口返回状态码: {}".format(response.status_code))
            resp_dict = trans_xml_to_dict(response.content)
            if resp_dict["return_code"] == "SUCCESS" and resp_dict["result_code"] == "SUCCESS":
                return HttpResponse(json.dumps(resp_dict), status=200)
            else:
                beary_chat("统一下单接口返回出错，请排查")
                return HttpResponse(json.dumps({"ret": 0, "data": "统一下单接口返回出错"}), status=500)
            # a = {'trade_type': u'JSAPI',
            #      'prepay_id': u'wx20171223152334f343581c200328355275',
            #      'nonce_str': u'Sr0LAd3XasY0l8aC',
            #      'return_code': u'SUCCESS',
            #      'return_msg': u'OK',
            #      'sign': u'2AC32D4662E7C2FC9984DCC224D54978',
            #      'mch_id': u'1481668232',
            #      'appid': u'wxb2e3e953b7f9c832',
            #      'result_code': u'SUCCESS'}
        except Exception as e:
            logger.error(e)


class SendAppTextMessage(View):
    @csrf_exempt
    def post(self, request):
        req_data = json.loads(request.body)
        phone_num = req_data.get('phone_num', None)

        p2 = re.compile('^1[34758]\\d{9}$')
        phone_match = p2.match(phone_num)
        if not phone_match:
            return HttpResponse(json.dumps({'data': '请确保输入正确的手机号码', 'ret': 0}), status=400)

        cache_key = phone_num + "_app_sms_send"
        verify_code = cache.get(cache_key)
        if verify_code is None:
            verify_code = random_num(length=6)

        message = '【良品福利折扣】验证码：' + verify_code

        cache.set(cache_key, verify_code, 300)
        for i in range(0, 100):
            if cache.get(cache_key) is None:
                return HttpResponse(json.dumps({'data': '缓存保存出错', 'ret': 0}), status=500)

        if not send_message(phoneNum=phone_num, message=message):
            return HttpResponse(json.dumps({'data': '短信发送失败', 'ret': 0}), status=500)

        return HttpResponse(json.dumps({'data': '短信发送成功,请查验', 'ret': 1}), status=200)


class AcceptNotifyView(View):
    def get(self, request):
        print "heihei"

    def post(self, request):
        print request.body










