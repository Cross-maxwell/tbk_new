# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import math
import random
import datetime
import json
from django.utils import timezone
import requests
from django.db import models
import fuli.top_settings
import top.api

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Entry(models.Model):
    create_time = models.DateTimeField(default=None)
    last_update = models.DateTimeField(default=None, db_index=True)
    # valid_until = models.DateTimeField(default=None)

    available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.create_time is None:
            self.create_time = timezone.now()
        self.last_update = timezone.now()
        super(Entry, self).save(*args, **kwargs)

    def get_text_msg(self):
        raise NotImplementedError('Should override get_text_msg().')

    def assert_available(self):
        raise NotImplementedError('Should override assert_available().')

    def get_img_msg(self):
        raise NotImplementedError('Should override get_img_msg().')


class PushRecord(models.Model):
    create_time = models.DateTimeField(auto_now=True)
    entry = models.ForeignKey('Entry')
    user_key = models.CharField(max_length=64)
    data_string = models.TextField(max_length=4096, default='')


class Product(Entry):
    # 商品标题
    title = models.CharField(max_length=256, db_index=True)
    # 商品描述
    desc = models.TextField(max_length=200)
    # 主图链接
    img_url = models.TextField(max_length=512)
    # 券面值
    cupon_value = models.FloatField()
    # 券后价格
    price = models.FloatField()
    # 30天销量
    sold_qty = models.IntegerField()
    # 剩余券数
    cupon_left = models.IntegerField()
    # 淘口令
    tao_pwd = models.CharField(max_length=32, null=True)
    # 优惠券链接
    cupon_url = models.TextField(max_length=1024)
    # Should be 优惠券的短链接。目前是直接与优惠券链接一致
    cupon_short_url = models.URLField(db_index=True, null=True)
    # 评论
    recommend = models.CharField(max_length=128, null=True)
    # 淘宝联盟给我司的佣金比率
    commision_rate = models.CharField('佣金比率',max_length=255, default='')
    # 淘宝联盟给我司的佣金
    commision_amount = models.FloatField(default=0)
    # 商品id
    item_id = models.CharField(max_length=64, unique=True, db_index=True, null=False)

    @property
    def org_price(self):
        return self.price + self.cupon_value

    @property
    def discount(self):
        return self.price / (self.cupon_value + self.price)

    @property
    def quality(self):
        return math.log(self.sold_qty)


    template = "{title}\n【原价】{org_price}元\n【券后】{price}元秒杀[闪电]!!\n【销售量】超过{sold_qty}件\n===============\n「打开链接，领取高额优惠券」\n{short_url}"
    template_end ="\n===============\n在群里直接发送“找XXX（你想要找的宝贝）”，我就会告诉你噢～\n「MMT一起赚」 天猫高额优惠，下单立减，你要的优惠都在这里～"
    def get_text_msg(self, pid=None):
        if pid is not None:
            if re.search('mm_\d+_\d+_\d+', self.cupon_url) is None:
                self.cupon_url = self.cupon_url + '&pid=' + pid
            else:
                self.cupon_url = re.sub(r'mm_\d+_\d+_\d+', pid, self.cupon_url)
            self.update_tokens()
        d = self.__dict__
        d.update({
            'org_price': self.org_price,
        })

        self.tao_pwd = self.tao_pwd[1:-1]

        """
        http://solesschong.gitee.io/yiqizhuan/index.html?tkl=2342
        """
        long_url = 'http://solesschong.gitee.io/yiqizhuan/index.html?tkl=%EF%BF%A5{0}%EF%BF%A5'.format(self.tao_pwd)
        # 微博short_url平台
        # source为ipad微博AppKey
        short_url_respose = requests.get(
            'http://api.weibo.com/2/short_url/shorten.json?source=2849184197&url_long=' + long_url)
        self.short_url = short_url_respose.json()['urls'][0]['url_short']

        msg = self.template.format(**self.__dict__)
        if self.cupon_left < 15:
            msg += u'\n该商品仅剩%s张券，抓紧下单吧！' % self.cupon_left
        msg += self.template_end
        if random.random() < 0.5:
            msg += u'\n本群招代理，如果你也想把优惠带给你身边的朋友，那就赶快加我私聊吧！'
        return msg

    def get_img_msg(self):
        return self.img_url

    def update_tokens(self):
        for _ in range(5):
            try:
                req = top.api.TbkTpwdCreateRequest()
                req.set_app_info(top.appinfo(fuli.top_settings.app_key, fuli.top_settings.app_secret))

                req.text = self.title.encode('utf-8')
                req.logo = self.img_url
                req.url = self.cupon_url

                resp = req.getResponse()
                self.tao_pwd = resp['tbk_tpwd_create_response']['data']['model']
                self.cupon_short_url = self.cupon_url
                break
            except Exception as e:
                print self.cupon_url, self.title
                print e.message
                continue

    def assert_available(self):
        if not self.available:
            return False
        if self.cupon_left <= 0:
            self.available = False
            print 'Trim item due to cupon left.'
        if self.sold_qty < 100 or (self.cupon_value / self.price) < 0.2:
            self.available = False
            print 'Trim item due to cupon value.'
        # elif self.cupon_left < 5:
        #     available = False
        #     print 'Trim item due to too few cupons left.'
        # elif re.search('mm_\d+_\d+_\d+', self.cupon_url) is None:
        #     self.available = False
        #     print 'Trim item due to no pid.'
        self.save()
        return self.available

    def save(self, *args, **kwargs):
        if self.last_update is None or \
                    timezone.now() - self.last_update > datetime.timedelta(days=5):
            self.update_tokens()
        try:
            self.item_id = re.search('itemId=(\d+)', self.cupon_url).groups()[0]
        except Exception:
            self.item_id = ''
        super(Product, self).save(*args, **kwargs)


class ProductDetail(Product):
    pass


class ProductCategory(models.Model):
    cat_name = models.CharField(max_length=128, null=True)
    cat_leaf_name = models.CharField(max_length=128, null=True)