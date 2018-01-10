# -*- coding: utf-8 -*-
import re
import random
import json
import time
import requests
import hashlib
import datetime
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache


from mini_program.settings import AppID, AppSecret, MCH_ID, IP, notify_url, prepay_url, refund_url
from mini_program.utils import get_sign_str, get_random_str, get_trade_num, get_64_random_number_string
from mini_program.utils import trans_dict_to_xml, trans_xml_to_dict, beary_chat
from broadcast.models.entry_models import Product
from mini_program.models.payment_models import Payment, AppUser, UserAddress, AppSession, PaymentOrder, NotifyPayment

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

        encryption_session_key = req_dict.get("encryption_session_key", "")
        goods_id = req_dict.get("goods_id", "")
        # TODO： 若要支持后台添加商品，则需要为该商品生成一个itemid，且该item_id必须在10位数以内
        item_id = req_dict.get("item_id", "")
        # 商品数量
        goods_num = req_dict.get("goods_num", "")
        # 商品名称
        goods_title = req_dict.get("goods_title", "")
        # 商品主图
        goods_img = req_dict.get("goods_img", "")

        # 用户备注
        remark = req_dict.get("remark", "")

        # 用户收货地址id
        address_id = req_dict.get("address_id", "")

        if not encryption_session_key or not goods_id or not item_id or not goods_num or \
                not goods_title or not goods_img or not address_id:
            return HttpResponse(json.dumps({"ret": 0, "data": "参数缺失"}), status=400)

        try:
            app_user = AppUser.objects.get(appsession__encryption_session_key=encryption_session_key)

            try:
                address = UserAddress.objects.get(app_user=app_user, id=address_id)
            except Exception as e:
                return HttpResponse(json.dumps({"ret": 0, "data": "地址不匹配或不存在"}, status=404))
            product = Product.objects.get(item_id=item_id, id=goods_id)

            out_trade_no = get_trade_num(item_id=item_id)

            # 订单总金额，单位为分，详见支付金额
            total_fee = int((product.price * int(goods_num)) * 100)
            payment_order_dict = {
                "goods_id": goods_id,
                "item_id": item_id,
                "goods_num": goods_num,
                "goods_title": goods_title,
                "goods_img": goods_img,
                "goods_price": product.price,
                "should_pay": total_fee,
                "app_user": app_user,
                "is_paid": False,
                "remark": remark,
                "out_trade_no": out_trade_no,
                "address_id": address_id
            }
            payment_order = PaymentOrder.objects.create(**payment_order_dict)
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({"ret": 0, "data": "商品或用户不存在"}, status=404))

        body = goods_title
        if len(body) > 128:
            body = body[:128]

        attach = "商品附加数据测试"
        nonce_str = get_random_str()

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
            "openid": app_user.openid
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
                param_data["payment_order"] = payment_order
                param_data.pop("openid")
                payment_db, created = Payment.objects.get_or_create(out_trade_no=out_trade_no, defaults=param_data)
                if not created:
                    return HttpResponse(json.dumps({"ret": 0, "data": "订单号{}已被创建，请勿重复提交".format(out_trade_no)}))

                # 将返回的数据再次进行签名，然后进行返回
                new_dict = {
                    "appId": resp_dict["appid"],
                    "timeStamp": int(time.time()),
                    "nonceStr": resp_dict["nonce_str"],
                    "package": "prepay_id=" + resp_dict["prepay_id"],
                    "signType": "MD5"
                }
                new_sorted_dict = sorted(new_dict.iteritems(), key=lambda x: x[0])

                pay_sign = get_sign_str(new_sorted_dict)

                new_dict["paySign"] = pay_sign
                return HttpResponse(json.dumps(new_dict), status=200)
            else:
                logger.error("统一下单接口返回出错, 原因：{}".format(json.dumps(resp_dict)))
                beary_chat("统一下单接口返回出错，请排查")
                return HttpResponse(json.dumps({"ret": 0, "data": "统一下单接口返回出错"}), status=500)
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({"ret": 0, "data": "服务器错误"}), status=500)


"""
appId, timeStamp, nonceStr, package, signType
"""
"""
支付完成后，微信会把相关支付结果和用户信息发送给商户，商户需要接收处理，并返回应答。

对后台通知交互时，如果微信收到商户的应答不是成功或超时，微信认为通知失败，微信会通过一定的策略定期重新发起通知，尽可能提高通知的成功率，
但微信不保证通知最终能成功。 （通知频率为15/15/30/180/1800/1800/1800/1800/3600，单位：秒）

注意：同样的通知可能会多次发送给商户系统。商户系统必须能够正确处理重复的通知。

推荐的做法是，当收到通知进行处理时，首先检查对应业务数据的状态，判断该通知是否已经处理过，如果没有处理过再进行处理，如果处理过直接返回结果成功。
在对业务数据进行状态检查和处理之前，要采用数据锁进行并发控制，以避免函数重入造成的数据混乱。

特别提醒：商户系统对于支付结果通知的内容一定要做签名验证,并校验返回的订单金额是否与商户侧的订单金额一致，防止数据泄漏导致出现“假通知”，造成资
金损失。

技术人员可登进微信商户后台扫描加入接口报警群。



"""


class AcceptNotifyURLView(View):
    def post(self, request):
        req_data = request.body
        req_data = """
            <xml><appid><![CDATA[wxb2e3e953b7f9c832]]></appid>
            <attach><![CDATA[商品附加数据测试]]></attach>
            <bank_type><![CDATA[CFT]]></bank_type>
            <cash_fee><![CDATA[1]]></cash_fee>
            <fee_type><![CDATA[CNY]]></fee_type>
            <is_subscribe><![CDATA[N]]></is_subscribe>
            <mch_id><![CDATA[1481668232]]></mch_id>
            <nonce_str><![CDATA[9QzGHIMRYKOdWZu1]]></nonce_str>
            <openid><![CDATA[oTOok0b1l7yJDvlS1VBVepbQrV0A]]></openid>
            <out_trade_no><![CDATA[1515228178531835587564wOjnu12J]]></out_trade_no>
            <result_code><![CDATA[SUCCESS]]></result_code>
            <return_code><!total_fee[CDATA[SUCCESS]]></return_code>
            <sign><![CDATA[FAA787E56264DEA58973641DA0FC2EAE]]></sign>
            <time_end><![CDATA[20180106164636]]></time_end>
            <total_fee>1</total_fee>
            <trade_type><![CDATA[JSAPI]]></trade_type>
            <transaction_id><![CDATA[4200000085201801069317628907]]></transaction_id>
            </xml>
        """
        req_dict = trans_xml_to_dict(req_data)

        out_trade_no = req_dict["out_trade_no"]
        notify_total_fee = req_dict["total_fee"]
        payment = Payment.objects.get(out_trade_no=out_trade_no)
        notify_sign = req_dict["sign"]

        req_dict.pop("sign")
        new_sorted_dict = sorted(req_dict.iteritems(), key=lambda x: x[0])

        check_sign = get_sign_str(new_sorted_dict)

        # 签名校验
        if notify_sign != check_sign:
            resp_dict = {
                "return_code": "FAIL",
                "return_msg": "签名校验失败"
            }
            resp_xml = trans_dict_to_xml(resp_dict)
            return HttpResponse(resp_xml)

        # 总金额校验
        if int(notify_total_fee) != payment.total_fee:
            resp_dict = {
                "return_code": "FAIL",
                "return_msg": "总金额校验失败"
            }
            resp_xml = trans_dict_to_xml(resp_dict)
            return HttpResponse(resp_xml)

        # 内部订单号校验
        if payment.out_trade_no != out_trade_no:
            resp_dict = {
                "return_code": "FAIL",
                "return_msg": "内部订单号校验失败"
            }
            resp_xml = trans_dict_to_xml(resp_dict)
            return HttpResponse(resp_xml)

        # 随机字符串校验
        if payment.nonce_str != req_dict["nonce_str"]:
            resp_dict = {
                "return_code": "FAIL",
                "return_msg": "随机字符串校验失败"
            }
            resp_xml = trans_dict_to_xml(resp_dict)
            return HttpResponse(resp_xml)


        new_dict = {
            "bank_type": req_dict["bank_type"],
            "cash_fee": req_dict["cash_fee"],
            "fee_type": req_dict["fee_type"],
            "result_code": req_dict["result_code"],
            "time_end": req_dict["time_end"],
            "total_fee": req_dict["total_fee"],
            "transaction_id": req_dict["transaction_id"],
            "payment": payment,
        }

        if req_dict["result_code"] == "SUCCESS":
            try:
                notify_payment, created = NotifyPayment.objects.get_or_create(payment=payment, defaults=new_dict)
                payment_order = PaymentOrder.objects.get(payment=payment)
                if payment_order:
                    payment_order.is_paid = True
                    payment_order.save()

                resp_dict = {
                    "return_code": "SUCCESS",
                    "return_msg": ""
                }
                resp_xml = trans_dict_to_xml(resp_dict)
                return HttpResponse(resp_xml)

            except Exception as e:
                logger.error(e)
                beary_chat("创建notify_payment失败, 原因: {}".format(e))
                resp_dict = {
                    "return_code": "FAIL",
                    "return_msg": "创建notify_payment失败"
                }
                resp_xml = trans_dict_to_xml(resp_dict)
                return HttpResponse(resp_xml)


class PaymentRefund(View):
    def post(self, request):
        req_dict = json.loads(request.body)

        encryption_session_key = req_dict.get("encryption_session_key", "")
        payment_order_id = req_dict.get("payment_order_id", "")
        app_user_id = req_dict.get("app_user_id", "")

        if not encryption_session_key or not payment_order_id or not app_user_id:
            return HttpResponse(json.dumps({"ret": 0, "data": "参数缺失"}), status=400)
        try:
            app_user = AppUser.objects.get(appsession__encryption_session_key=encryption_session_key)
        except Exception as e:
            return HttpResponse(json.dumps({"ret": 0, "data": "用户不存在"}), status=400)

        # 只有is_paid的订单才能够退款
        try:
            payment_order = PaymentOrder.objects.get(id=payment_order_id, app_user__id=app_user_id)
            if not payment_order.is_paid:
                return HttpResponse(json.dumps({"ret": 0, "data": "订单不存在"}), status=400)
        except PaymentOrder.DoesNotExist:
            return HttpResponse(json.dumps({"ret": 0, "data": "订单不存在"}), status=400)
        except PaymentOrder.MultipleObjectsReturned:
            beary_chat("PaymentOrder表出现严重问题，请排查")
            return HttpResponse(json.dumps({"ret": 0, "data": "订单不存在"}), status=400)

        try:
            # 微信返回的交易id
            transaction_id = NotifyPayment.objects.get(payment__payment_order=payment_order).transaction_id
        except PaymentOrder.DoesNotExist:
            return HttpResponse(json.dumps({"ret": 0, "data": "订单不存在"}), status=400)
        except PaymentOrder.MultipleObjectsReturned:
            beary_chat("NotifyPayment表出现严重问题，请排查")
            return HttpResponse(json.dumps({"ret": 0, "data": "订单不存在"}), status=400)

        nonce_str = get_random_str()

        # 商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔
        out_refund_no = get_64_random_number_string()

        # 订单总金额，单位为分，只能为整数，详见支付金额
        total_fee = payment_order.should_pay

        # 退款总金额，订单总金额，单位为分，只能为整数，详见支付金额
        refund_fee = total_fee

        # 操作员帐号, 默认为商户号
        op_user_id = MCH_ID

        param_data = {
            "appid": AppID,
            "mch_id": MCH_ID,
            # 随机字符串，不长于32位。推荐随机数生成算法
            "nonce_str": nonce_str,
            "transaction_id": transaction_id,
            # 商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔
            "out_refund_no": out_refund_no,
            "total_fee": total_fee,
            # 退款总金额，订单总金额，单位为分，只能为整数，详见支付金额
            "refund_fee": total_fee,
            # 操作员，默认为商户号
            "op_user_id": op_user_id
        }

        sorted_dict = sorted(param_data.iteritems(), key=lambda x: x[0])
        sign = get_sign_str(sorted_dict)
        param_data["sign"] = sign

        # 这里写XML是真的蠢，什么年代了还用这种鬼东西
        req_xml_data = trans_dict_to_xml(param_data)
        try:
            response = requests.post(refund_url, data=req_xml_data, headers={'Content-Type': 'text/xml'})
            logger.info("退款接口返回状态码: {}".format(response.status_code))
            resp_dict = trans_xml_to_dict(response.content)
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





"""
'1', '某某某', 'http://', 'string', 'China', 'string', 'oTOok0b1l7yJDvlS1VBVepbQrV0A', '2018-01-06 03:04:59.540533'
'1', 'YXD+IgoU93abZz/6IqHM6w==', 'dccf6e5eb5e92692dc44a5e7bd729a765ce9063ca5df92724192fdd7f60abfd36368436f8a3b6076dae094a5db6867188811996e6c28cb441def731289479f5e', '2018-02-05 03:05:02.058583', '1'


"""




