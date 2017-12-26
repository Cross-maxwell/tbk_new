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
    session_key encryption_session_key expire_day app_user[id]
那么，前端能够拿到的数据有什么？
"""


class PrepayView(View):
    def post(self, request):
        req_dict = json.loads(request.body)

        openid = req_dict.get("openid", "")
        goods_id = req_dict.get("goods_id", "")
        item_id = req_dict.get("item_id", "")
        # 商品数量
        goods_num = req_dict.get("goods_num", "")
        # 商品名称
        goods_title = req_dict.get("goods_title", "")

        if not (openid or goods_id or item_id or goods_num or goods_title):
            return HttpResponse(json.dumps({"ret": 0, "data": "参数缺失"}), status=400)

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
            "mch_id": MCH_ID,
            # 随机字符串，不长于32位。推荐随机数生成算法
            "nonce_str": nonce_str,
            # 商品简单描述，该字段须严格按照规范传递，具体请见参数规定， 最长128位， 即最长40个中文
            "body": body,
            # 商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号,必须唯一
            "out_trade_no": out_trade_no,
            "total_fee": total_fee,
            "spbill_create_ip": IP,
            "notify_url": notify_url,
            # 附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
            "attach": attach,
            "trade_type": "JSAPI",
            "openid": openid
        }
        sorted_dict = sorted(param_data.iteritems(), key=lambda x: x[0])
        sign = get_sign_str(sorted_dict)
        param_data["sign"] = sign

        # 这里写XML是真的蠢，什么年代了还用这种鬼东西
        req_xml_data = trans_dict_to_xml(param_data)
        try:
            response = requests.post(prepay_url, data=req_xml_data, headers={'Content-Type': 'text/xml'})
            logger.info("统一下单接口返回状态码: {}".format(response.status_code))
            resp_dict = trans_xml_to_dict(response.content)
            if resp_dict["return_code"] == "SUCCESS" and resp_dict["result_code"] == "SUCCESS":
                payment_db, created = Payment.objects.get_or_create(out_trade_no=out_trade_no, defaults=param_data)
                if not created:
                    return HttpResponse(json.dumps({"ret": 0, "data": "订单号{}已被创建，请勿重复提交".format(out_trade_no)}))
                resp_dict.pop("mch_id")
                return HttpResponse(json.dumps(resp_dict), status=200)
            else:
                logger.error("统一下单接口返回出错, 原因：{}".format(json.dumps(resp_dict)))
                beary_chat("统一下单接口返回出错，请排查")
                return HttpResponse(json.dumps({"ret": 0, "data": "统一下单接口返回出错"}), status=500)
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({"ret": 0, "data": "服务器错误"}), status=500)


class AcceptNotifyURLView(View):
    def post(self, request):
        req_data = request.body
        req_dict = trans_xml_to_dict(req_data)
        print req_dict

        """
        接受数据
        <xml>
          <appid><![CDATA[wx2421b1c4370ec43b]]></appid>
          <attach><![CDATA[支付测试]]></attach>
          <bank_type><![CDATA[CFT]]></bank_type>
          <fee_type><![CDATA[CNY]]></fee_type>
          <is_subscribe><![CDATA[Y]]></is_subscribe>
          <mch_id><![CDATA[10000100]]></mch_id>
          <nonce_str><![CDATA[5d2b6c2a8db53831f7eda20af46e531c]]></nonce_str>
          <openid><![CDATA[oUpF8uMEb4qRXf22hE3X68TekukE]]></openid>
          <out_trade_no><![CDATA[1409811653]]></out_trade_no>
          <result_code><![CDATA[SUCCESS]]></result_code>
          <return_code><![CDATA[SUCCESS]]></return_code>
          <sign><![CDATA[B552ED6B279343CB493C5DD0D78AB241]]></sign>
          <sub_mch_id><![CDATA[10000100]]></sub_mch_id>
          <time_end><![CDATA[20140903131540]]></time_end>
          <total_fee>1</total_fee>
          <coupon_fee><![CDATA[10]]></coupon_fee>
          <coupon_count><![CDATA[1]]></coupon_count>
          <coupon_type><![CDATA[CASH]]></coupon_type>
          <coupon_id><![CDATA[10000]]></coupon_id>
          <coupon_fee><![CDATA[100]]></coupon_fee>
          <trade_type><![CDATA[JSAPI]]></trade_type>
          <transaction_id><![CDATA[1004400740201409030005092168]]></transaction_id>
        </xml>
        
        返回数据
        <xml>
          <return_code><![CDATA[SUCCESS]]></return_code>
          <return_msg><![CDATA[OK]]></return_msg>
        </xml>
        """










































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










