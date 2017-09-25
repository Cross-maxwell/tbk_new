# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import math
import datetime
import json
from django.utils import timezone
import requests
from django.db import models
import fuli.top_settings
# from top import top.api
import random
import top.api


class Entry(models.Model):
    create_time = models.DateTimeField(default=None)
    last_update = models.DateTimeField(default=None)
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
    group = models.CharField(max_length=64)
    data_string = models.TextField(max_length=4096, default='')


class Product(Entry):
    title = models.CharField(max_length=256, db_index=True)
    desc = models.TextField(max_length=200)
    img_url = models.TextField(max_length=512)

    # 券面值
    cupon_value = models.FloatField()
    # 券后价格
    price = models.FloatField()
    # 30天销量
    sold_qty = models.IntegerField()
    # 剩余券数
    cupon_left = models.IntegerField()

    tao_pwd = models.CharField(max_length=32, null=True)
    cupon_url = models.TextField(max_length=1024)
    cupon_short_url = models.URLField(db_index=True, null=True)

    recommend = models.CharField(max_length=128, null=True)

    @property
    def org_price(self):
        return self.price + self.cupon_value

    @property
    def discount(self):
        return self.price / (self.cupon_value + self.price)

    @property
    def quality(self):
        return math.log(self.sold_qty)

    item_id = models.CharField(max_length=64, unique=True, db_index=True, null=False)


    template = \
"""{title}
【标价】{org_price}元
【本群价】￥{price}!!
【已疯抢】超过{sold_qty}件
-----------------
{desc}  下单地址： {short_url}"""
    update_tao_pwd_url = 'http://www.fuligou88.com/haoquan/details_show00.php?act=zhuan'

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
        """
        添加encode是否合适？
        """
        long_url = 'https://yiqizhuang.github.io/index.html?tkl=%EF%BF%A5{0}%EF%BF%A5'.format(self.tao_pwd)
        # short_url_respose = requests.get('http://goo.gd/action/json.php?source=1681459862&url_long=' + long_url)

        # 微博short_url平台
        # source 为ipad微博AppKey
        short_url_respose = requests.get('http://api.weibo.com/2/short_url/shorten.json?source=2849184197&url_long=' + long_url)
        self.short_url = short_url_respose.json()['urls'][0]['url_short']

        msg = self.template.format(**self.__dict__)
        if self.cupon_left < 15:
            msg += u'\n（该商品仅剩%s张券，抓紧下单吧）' % self.cupon_left
        if random.random() < 0.1:
            msg += u'\n本群招代理，如果你也想把优惠带给你身边的朋友，那就赶快加我私聊吧！'
        print self.cupon_url
        return msg

    def get_img_msg(self):
        return self.img_url

    def update_tokens(self):
        for _ in range(5):
            try:
                req = top.api.WirelessShareTpwdCreateRequest()
                req.set_app_info(top.appinfo(fuli.top_settings.app_key, fuli.top_settings.app_secret))

                req.tpwd_param = json.dumps({
                    'url': self.cupon_url,
                    'text': self.title,
                    'logo': self.img_url,
                })
                resp = req.getResponse()

                self.tao_pwd = resp['wireless_share_tpwd_create_response']['model']

                self.cupon_short_url = self.cupon_url
                break
            except Exception:
                print self.cupon_url, self.title
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
