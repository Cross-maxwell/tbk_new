# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import math
import random
import datetime
import json
import requests
import urllib2

from django.utils import timezone
from django.db import models
from broadcast.utils.image_connect import generate_image, generate_qrcode
from django.dispatch import receiver
from django.db.models.signals import post_save
from broadcast.utils.entry_utils import get_item_info

import fuli.top_settings
import top.api

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging
logger = logging.getLogger('django_models')


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

    @property
    def p(self):
        try:
            return self.product
        except AttributeError:
            return self.jdproduct


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
    # 推广图链接
    send_img = models.TextField(max_length=512, null=True)
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
    # 商品分类
    cate = models.CharField(max_length=128, null=True, db_index=True)

    # 商品推广文案
    broadcast_text = models.CharField(max_length=4096, default="")
    # 商品推广图片
    broadcast_img = models.CharField(max_length=4096, default="[]")

    @property
    def org_price(self):
        return self.price + self.cupon_value

    @property
    def discount(self):
        return self.price / (self.cupon_value + self.price)

    @property
    def quality(self):
        return math.log(self.sold_qty)

    # def get_text_msg_wxapp(self):
    #     recommend = ''
    #     try:
    #         recommend = self.productdetail.recommend
    #     except Exception as e:
    #         logger.error(e.message)
    #     key_title = random.choice(['折扣商品', '秒杀单品', '热门爆款'])
    #     key_sold = random.choice(['销售数量', '已售出', '已抢购', '已疯抢'])
    #     key_cupon = random.choice(['剩余券数', '优惠券还剩', '优惠券数量'])
    #     key_recommend = random.choice(['推荐理由' ,'优质推荐'])
    #     template = "【{key_title}】：{title}\n" \
    #                 "【{key_sold}】：{sold_qty}\n" \
    #                 "【{key_cupon}】：{cupon_left}\n"
    #     if recommend:
    #         template = template + "【{key_recommend}】：{recommend}\n"
    #     if random.randrange(1, 5) == 1:
    #         template = template + "===============\n" \
    #                                   "下单方式：点开任意图片，长按识别图中小程序码\n" \
    #                                   "===============\n" \
    #                                   "在群里直接发送“找XXX（例如：找手机）”，我就会告诉你噢～"
    #     return template.format(**dict(self.__dict__, **{
    #         'key_title': key_title,
    #         'key_sold': key_sold,
    #         'key_cupon': key_cupon,
    #         'key_recommend': key_recommend,
    #         'recommend': recommend
    #     }))

    def get_text_msg_wxapp(self):
        recommend = ''
        try:
            recommend = self.productdetail.recommend
        except Exception as e:
            logger.error(e.message)
        key_org_price = '在售价'
        key_price = '券后价'
        template = "{title}\n" \
                   "【{key_org_price}】：{org_price}\n" \
                   "【{key_price}】：{price}\n"
        if recommend:
            template = template + "{recommend}\n"
        if random.randrange(1, 5) == 1:
            template = template + "===============\n" \
                                      "下单方式：点开任意图片，长按识别图中小程序码\n" \
                                      "===============\n" \
                                      "在群里直接发送“找XXX（例如：找手机）”，我就会告诉你噢～"
        return template.format(**dict(self.__dict__, **{
            'key_org_price': key_org_price,
            'key_price': key_price,
            'recommend': recommend,
            'org_price': self.org_price,
        }))

    def get_img_msg_wxapp(self, pid=None, tkuser_id=None):
        # 使用pid 更新淘口令
        if pid is not None:
            if re.search('mm_\d+_\d+_\d+', self.cupon_url) is None:
                self.cupon_url = self.cupon_url + '&pid=' + pid
            else:
                self.cupon_url = re.sub(r'mm_\d+_\d+_\d+', pid, self.cupon_url)
            # self.update_tokens()
        self.tao_pwd = self.get_tkl(pid)[1:-1]

        # 使用id, 淘口令, 图片链接 获取小程序二维码及商品的拼接图片
        # 便于复用，首先调用生成wxapp二维码
        req_data = {
            "page": "pages/goods/goods",
            "scene": "{0}${1}${2}".format(self.id, self.tao_pwd, tkuser_id)
        }

        logger.info("生成小程序二维码: product_id: {0}, tkl: {1}".format(self.id, self.tao_pwd))
        qrcode_flow = generate_qrcode(req_data)
        product_url_list = [self.img_url]
        # 原价，优选价，优惠卷价
        price_list = [round(self.org_price, 2), round(self.price, 2), round(self.cupon_value, 2)]
        # try:
        #     product_detail = ProductDetail.objects.filter(product_id=self.id).first()
        #     if product_detail:
        #         small_img_list = json.loads(product_detail.small_imgs)
        #         img_list = [item for item in small_img_list if item.endswith("png") or item.endswith("jpg")][:2]
        #         if len(img_list) == 2 and self.is_img_alive(img_list):
        #             product_url_list += img_list
        # except Exception as e:
        #     logger.error(e)
        return generate_image(product_url_list, qrcode_flow, price_list, title=self.title)

    def is_img_alive(self, img_list):
        for i in range(2):
            try:
                test_data = urllib2.urlopen(img_list[i]).read()
            except:
                return False
        return True

    def get_tkl(self, pid):
        # tkl_url = "http://dianjin.dg15.cn/a_api/index/getTpwd"
        pattern = ".*(?:activity_id|activityId)=(.*)"
        result = re.match(pattern, self.cupon_url)
        if result:
            activityId = result.group(1)
            # data = {
            #     "itemId": self.item_id,
            #     "activityId": activityId,
            #     "pid": pid,
            #     "image": self.img_url,
            #     "title": self.title,
            #     "sellerId": self.productdetail.seller_id
            # }
            # headers = {
            #     "Content-Type": "application/x-www-form-urlencoded"
            # }
            # tkl_response = requests.post(tkl_url, data=data, headers=headers)
            # res_dict = json.loads(tkl_response.content)
            # tkl = res_dict["status"]["msg"]
            return self.__get_tkl_from_dianjin(activityId, pid)
        else:
            # logger.error("匹配activityId失败")
            return self.__get_tkl_from_sdk(pid)
            # return tkl

    def __get_tkl_from_dianjin(self, activityId, pid):
        tkl_url = "http://dianjin.dg15.cn/a_api/index/getTpwd"
        data = {
            "itemId": self.item_id,
            "activityId": activityId,
            "pid": pid,
            "image": self.img_url,
            "title": self.title,
            "sellerId": self.productdetail.seller_id
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        tkl_response = requests.post(tkl_url, data=data, headers=headers)
        res_dict = json.loads(tkl_response.content)
        tkl = res_dict["status"]["msg"]
        return tkl

    def __get_tkl_from_sdk(self, activityId, pid):
        for _ in range(5):
            try:
                req = top.api.TbkTpwdCreateRequest()
                req.set_app_info(top.appinfo(fuli.top_settings.app_key, fuli.top_settings.app_secret))

                req.text = self.title.encode('utf-8')
                req.logo = self.img_url
                req.url = "https://uland.taobao.com/coupon/edetail?activityId={}&itemId={}&pid={}&src=qunmi"\
                            .format(activityId, self.item_id, pid)
                req.url = re.sub('pid=([\d\w_]+)', 'pid=' + pid, req.url)

                resp = req.getResponse()
                tkl = resp['tbk_tpwd_create_response']['data']['model']
                return tkl
            except Exception as e:
                logger.error(e.message)
                continue

    """旧的获取文字及图片的方法，不用了"""
    # template = "{title}\n【原价】{org_price}元\n【券后】{price}元秒杀[闪电]!!\n【销售量】超过{sold_qty}件\n===============\n「打开链接，领取高额优惠券」\n{short_url}"
    # template_end ="\n===============\n在群里直接发送“找XXX（你想要找的宝贝）”，我就会告诉你噢～\n「MMT一起赚」 高额优惠，下单立减，你要的优惠都在这里～"
    #
    # def get_text_msg(self, pid=None):
    #     if pid is not None:
    #         if re.search('mm_\d+_\d+_\d+', self.cupon_url) is None:
    #             self.cupon_url = self.cupon_url + '&pid=' + pid
    #         else:
    #             self.cupon_url = re.sub(r'mm_\d+_\d+_\d+', pid, self.cupon_url)
    #         # self.update_tokens()
    #     self.tao_pwd = self.get_tkl(pid)[1:-1]
    #     # self.tao_pwd = self.tao_pwd[1:-1]
    #
    #     """
    #     http://solesschong.gitee.io/yiqizhuan/index.html?tkl=2342
    #     """
    #     long_url = 'http://solesschong.gitee.io/yiqizhuan/index.html?tkl=%EF%BF%A5{0}%EF%BF%A5'.format(self.tao_pwd)
    #     # 微博short_url平台
    #     # source为ipad微博AppKey
    #     short_url_respose = requests.get(
    #         'http://api.weibo.com/2/short_url/shorten.json?source=2849184197&url_long=' + long_url)
    #     self.short_url = short_url_respose.json()['urls'][0]['url_short']
    #
    #     msg = self.template.format(**self.__dict__)
    #     if self.cupon_left < 15:
    #         msg += u'\n该商品仅剩%s张券，抓紧下单吧！' % self.cupon_left
    #     msg += self.template_end
    #     if random.random() < 0.5:
    #         msg += u'\n本群招代理，如果你也想把优惠带给你身边的朋友，那就赶快加我私聊吧！'
    #     return msg
    #
    # def get_img_msg(self):
    #     return self.img_url

    """update_token不用了"""
    # def update_tokens(self):
    #     for _ in range(5):
    #         try:
    #             req = top.api.TbkTpwdCreateRequest()
    #             req.set_app_info(top.appinfo(fuli.top_settings.app_key, fuli.top_settings.app_secret))
    #
    #             req.text = self.title.encode('utf-8')
    #             req.logo = self.img_url
    #             req.url = self.cupon_url
    #
    #             resp = req.getResponse()
    #             self.tao_pwd = resp['tbk_tpwd_create_response']['data']['model']
    #             self.cupon_short_url = self.cupon_url
    #             break
    #         except Exception as e:
    #             print self.cupon_url, self.title
    #             print e.message
    #             continue

    def assert_available(self):
        self.available = True
        # 2018.01.05 改用懒懒的API后，其返回的剩余券数似乎有问题， 即使显示0也可正常领取，
        # 因调用API时排序规则为按更新时间排序， 没有优惠券的可能性较小。
        # 经测试，即使第50页剩余券数为0的商品依旧可以正常领券。。。
        if self.cupon_left <= 0:
            self.available = False
            print 'Trim item due to cupon left.'
        # 2017.12.27 19:41 王培钦: 折扣力度小于0.1时判不可用（原为0.2）
        if self.sold_qty < 100 or (self.cupon_value / self.price) < 0.1:
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

    # def save(self, *args, **kwargs):
    #     # if self.last_update is None or \
    #     #             timezone.now() - self.last_update > datetime.timedelta(days=5):
    #     #     # self.update_tokens()
    #     # try:
    #     #     self.item_id = re.search('itemId=(\d+)', self.cupon_url).groups()[0]
    #     # except Exception:
    #     #     self.item_id = ''
    #     super(Product, self).save(*args, **kwargs)


class ProductDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    # 卖家地址， 从详情接口取得
    provcity = models.CharField(max_length=64, null=True)
    # 商品链接，从详情接口取得
    item_url = models.CharField(max_length=128, null=True)
    # 卖家ID ，从详情接口取得
    seller_id = models.CharField(max_length=128)
    # 卖家昵称，从详情接口取得
    seller_nick = models.CharField(max_length=256)
    # 小图，从详情接口取得
    small_imgs = models.TextField(max_length=16383, default='[]')
    # 类别，外键关联到ProductCategory模型
    # cate = models.ForeignKey('ProductCategory')
    # 商品描述图片
    describe_imgs = models.TextField(max_length=16383, default='[]')
    # 商品描述/推荐理由
    recommend = models.CharField(max_length=4096, default='')


class JDProduct(Entry):
    """
    京东商品，与淘宝商品字段名尽量保持一致。
    """
    # 商品id
    item_id = models.CharField(max_length=64, unique=True, db_index=True)
    # 商品标题
    title = models.CharField(max_length=128)
    # 商品描述
    desc = models.CharField(max_length=1024)
    # 商品链接
    item_url = models.CharField(max_length=1024)
    # 主图
    img_url = models.CharField(max_length=1024)
    # 券后价
    price = models.FloatField()
    # 券面值
    cupon_value = models.FloatField()
    # 总销量
    sold_qty = models.IntegerField()
    # 佣金比例
    commision_rate = models.FloatField()
    # 佣金金额
    commision_amount = models.FloatField()
    # 优惠券链接
    cupon_url = models.CharField(max_length=1024)
    # 分类
    cate = models.CharField(max_length=128)

    #原价
    @property
    def org_price(self):
        return self.price + self.cupon_value

    def get_text_msg_wxapp(self):
        key_title = random.choice(['折扣商品', '秒杀单品', '热门爆款'])
        key_sold = random.choice(['销售数量', '已售出', '已抢购', '已疯抢'])
        key_recommend = random.choice(['推荐理由' ,'优质推荐'])
        template = "【{key_title}】：{title}\n" \
                    "【{key_sold}】：{sold_qty}\n" \
                   "【{key_recommend}】：{desc}\n"
        if random.randrange(1, 5) == 1:
            template = template + "===============\n" \
                                      "下单方式：点开任意图片，长按识别图中小程序码\n" \
                                      "===============\n" \
                                      "在群里直接发送“找XXX（例如：找手机）”，我就会告诉你噢～"
        return template.format(**dict(self.__dict__, **{
            'key_title': key_title,
            'key_sold': key_sold,
            'key_recommend': key_recommend,
            'sold_qty': random.randint(100,2000)
        }))


    def get_img_msg_wxapp(self, pid=None, tkuser_id=None):
        req_data = {
            "page": "pages/goods/goods",
            "scene": "{0}${1}${2}".format(self.id, 'f', tkuser_id)
        }
        qrcode_flow = generate_qrcode(req_data)
        product_url_list = [self.img_url]
        price_list = [round(self.org_price, 2), round(self.price, 2)]
        return generate_image(product_url_list, qrcode_flow, price_list)


    def get_short_url(self, pid='1133349744'):
        short_url_api = 'http://www.haojingke.com/index.php/api/index/myapi?type=unionurl&' \
                        'apikey={api_key}&' \
                        'materialIds={item_id}&' \
                        'couponUrl={cupon_url}&' \
                        'positionId={pid}'.format(
            api_key=fuli.top_settings.hjk_apikey,
            item_id = self.item_id,
            cupon_url = self.cupon_url,
            pid = pid
        )
        resp = requests.get(short_url_api, headers={'Connection':'close'})
        return resp.json()['data']

    def save(self, *args, **kwargs):
        if self.cupon_value/self.org_price < 0.2:
            self.available = False
        super(JDProduct, self).save(*args, **kwargs)

class SearchKeywordMapping(models.Model):
    username = models.CharField(max_length=200)
    keyword = models.CharField(max_length=200)