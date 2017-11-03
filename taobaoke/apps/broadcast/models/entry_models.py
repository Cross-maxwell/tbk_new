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


#     template = \
# """
# 【商品名称】{title}
# 【券后劲爆价】￥{price}
# 【劲省】{cupon_value}元!!
# -----------------
# {desc}
# 【淘口令】{tao_pwd}
# 复制这条消息，打开“手机淘宝”即可领券之后再下单
# 也可以点击此链接直接下单：{cupon_url}
# """

#     template = \
# """{title}
# 【标价】{org_price}元
# 【本群价】￥{price}!!
# 【已疯抢】超过{sold_qty}件
# -----------------
# {desc}  下单地址： {short_url} """

    template = "{title}\n【原价】{org_price}元\n【券后】{price}元秒杀[闪电]!!\n【销售量】超过{sold_qty}件\n===============\n「打开链接，领取高额优惠券」\n{short_url}"
    template_end ="\n===============\n在群里直接发送“找XXX（你想要找的宝贝）”，我就会告诉你噢～\n「MMT一起赚」 天猫高额优惠，下单立减，你要的优惠都在这里～"

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

        self.tao_pwd = self.tao_pwd[1:-1]


        long_url = 'https://yiqizhuang.github.io/index.html?tkl=%EF%BF%A5{0}%EF%BF%A5'.format(self.tao_pwd)
        # 微博short_url平台
        # source为ipad微博AppKey
        short_url_respose = requests.get(
            'http://api.weibo.com/2/short_url/shorten.json?source=2849184197&url_long=' + long_url)
        self.short_url = short_url_respose.json()['urls'][0]['url_short']

        msg = self.template.format(**self.__dict__)
        if self.cupon_left < 15:
            msg += u'\n该商品仅剩%s张券，抓紧下单吧！' % self.cupon_left
        msg += self.template_end
        # if random.random() < 0.5:
        #     msg += u'\n本群招代理，如果你也想把优惠带给你身边的朋友，那就赶快加我私聊吧！'
        # print self.cupon_url
        msg_activity = '\n天猫双十一现金红包雨来啦，最高抢￥1111元现金，红包每天都能抢，但每日红包数量有限，速速来抢！\nhttp://dianjin.dg15.cn/x/2bffc315 '
        rate = random.random()
        if rate <= 0.5:
            msg += msg_activity
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



