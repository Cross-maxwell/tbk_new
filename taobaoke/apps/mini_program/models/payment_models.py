# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class AppUser(models.Model):
    nickname = models.CharField(max_length=128)
    avatar_url = models.URLField()
    city = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    province = models.CharField(max_length=128)
    openid = models.CharField(max_length=50, unique=True)

    created = models.DateTimeField(auto_now_add=True)


class AppSession(models.Model):
    session_key = models.CharField(max_length=128)
    # 加密后session_key
    encryption_session_key = models.CharField(max_length=255, unique=True)
    # encryption_session_key过期时间
    expire_day = models.DateTimeField(default=None)
    app_user = models.OneToOneField(AppUser)


class UserAddress(models.Model):
    phone_num = models.CharField(max_length=11)
    name = models.CharField(max_length=25)
    address = models.TextField()

    app_user = models.ForeignKey(AppUser)
    created = models.DateTimeField(auto_now_add=True)

    def update_from_dict(self, msg_dict):
        self.phone_num = msg_dict["phone_num"]
        self.name = msg_dict["name"]
        self.address = msg_dict["address"]


class PaymentOrder(models.Model):
    # 商品id
    goods_id = models.CharField(max_length=100)
    # 商品标识id
    item_id = models.CharField(max_length=100)
    # 商品数量
    goods_num = models.IntegerField()
    # 商品价格
    goods_price = models.FloatField()
    # 应付金额
    should_pay = models.FloatField()
    # 商品标题
    goods_title = models.TextField()

    app_user = models.ForeignKey(AppUser)

    # 是否已付款
    is_paid = models.BooleanField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Payment(models.Model):
    appid = models.CharField(max_length=100)
    # 附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
    attach = models.CharField(max_length=255)
    # 商品简单描述，该字段须严格按照规范传递，具体请见参数规定， 最长128位， 即最长40个中文
    body = models.CharField(max_length=255)
    # 微信支付分配的商户号
    mch_id = models.CharField(max_length=50)
    # 随机字符串，不长于32位。推荐随机数生成算法
    nonce_str = models.CharField(max_length=32)
    # 接收微信支付异步通知回调地址，通知url必须为直接可访问的url，不能携带参数。
    notify_url = models.CharField(max_length=255)
    # 商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号,必须唯一
    out_trade_no = models.CharField(max_length=32, unique=True)
    # APP和网页支付提交用户端ip，Native支付填调用微信支付API的机器IP。
    spbill_create_ip = models.CharField(max_length=25)
    trade_type = models.CharField(max_length=20)
    # 签名，详见签名生成算法
    sign = models.CharField(max_length=255)
    # 单位为分
    total_fee = models.IntegerField()

    payment_order = models.OneToOneField(PaymentOrder)
    created = models.DateTimeField(auto_now_add=True)


class NotifyPayment(models.Model):
    # 银行类型
    bank_type = models.CharField(max_length=20)
    # 支付现金
    cash_fee = models.IntegerField()
    # 现金类型
    fee_type = models.CharField(max_length=20)
    # 处理结果
    result_code = models.CharField(max_length=20)
    time_end = models.CharField(max_length=36)
    # 订单金额
    total_fee = models.IntegerField()
    # 微信支付id
    transaction_id = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    payment = models.OneToOneField(Payment)

