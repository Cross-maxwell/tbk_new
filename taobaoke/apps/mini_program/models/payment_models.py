# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class AppUser(models.Model):
    nickname = models.CharField(max_length=128)
    avatar_url = models.URLField()
    city = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    province = models.CharField(max_length=128)
    openid = models.CharField(max_length=50, default="")


class AppSession(models.Model):
    session_key = models.CharField(max_length=128)
    # 加密后session_key
    encryption_session_key = models.CharField(max_length=255)
    # encryption_session_key过期时间
    expire_day = models.DateTimeField(default=None)
    app_user = models.OneToOneField(AppUser)


class UserAddress(models.Model):
    phone_num = models.CharField(max_length=11)
    name = models.CharField(max_length=25)
    address = models.TextField()

    app_user = models.ForeignKey(AppUser)

    created = models.DateTimeField(auto_now=True)


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
    out_trade_no = models.CharField(max_length=32)
    # APP和网页支付提交用户端ip，Native支付填调用微信支付API的机器IP。
    spbill_create_ip = models.CharField(max_length=25)
    trade_type = models.CharField(max_length=20)
    # 签名，详见签名生成算法
    sign = models.CharField(max_length=255)

    # 单位为分
    total_fee = models.IntegerField()

    app_user = models.OneToOneField(AppUser)

    created = models.DateTimeField(auto_now=True)