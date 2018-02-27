# coding: utf-8
"""
本包中包括处理第三方消息的功能，输入为字符串形式
来源：
1. QQ 淘宝客-万群粑粑 2018.02.08

"""
import re
import requests
import time
from datetime import datetime, timedelta
from selenium import webdriver
# PHANTOMJS_PATH = '/home/adam/mydev/tools/phantomjs/bin/phantomjs'
# todo : PhantomJs Path On 07 , To Be Confirmed
PHANTOMJS_PATH = '/home/phantomjs/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'

from django.db import connection
from enum import Enum
from fuli.top_settings import lanlan_apikey
from broadcast.models.entry_models import Product
from broadcast.utils.entry_utils import get_item_info, get_cupon_info
from scripts.goods.fetch_lanlan import update_productdetails

import logging
logger = logging.getLogger('post_taobaoke')


class ThirdMsg(object):
    """
    预留扩展空间，作为所有第三方消息来源的基类
    继承出的子类应包含对具体来源信息的处理方法，强制要求重写parse方法。
    """
    def __init__(self, msg):
        self.msg = msg

    def parse(self):
        raise NotImplementedError('Should be overriden.')


class WQMsg(ThirdMsg):
    """
    针对万群粑粑的，发出消息是商品、领券双链接的淘宝客推广
    每个WQMsg实例代表一个商品
    """
    # 使用此枚举类用以维护商品来源
    item_sources = Enum('item_source', ('lanlan', 'other'))

    def __init__(self, msg):
        super(WQMsg, self).__init__(msg)
        self.item_url = None
        self.img_url = None
        self.item_id = None
        self.item_source = None
        self.product_dict = None

    def reorganize(self):
        """
        若未解析到商品，调用此方法，将消息重组并转发
        :return: data, 由图片url和文字组合形成的消息列表
        """
        data = []
        img_url = self.__get_img_and_remove()
        if img_url:
            data.append(img_url)
        data.append(self.msg)
        return data

    def __get_img_and_remove(self):
        """
        仅用于消息转发， 获取图片链接并删除代表图片的文本
        :return:
        """
        img_url_pattern = re.compile('\[CQ:image,file=(https?://[.\d\w\./\?=&;\\%~]+)\]')
        try:
            img_url = img_url_pattern.findall(self.msg)[0]
        except IndexError:
            img_url = None
        except Exception as e:
            logger.error(e)
            img_url = None
        finally:
            img_file_pattern = re.compile('(\[CQ:image,file=https?://[.\d\w\./\?=&;\\%~]+\])')
            self.msg = img_file_pattern.sub('', self.msg)
            return img_url

    def parse(self):
        """
        解析商品并存库
        :return:
        """
        try:
            self.__get_urls()
            self.__get_img()
            self.__get_item_id()
            self.__fetch_detail()
            self.save_from_product_dict(self.product_dict)
            return self.item_id
        except NoItemException:
            raise
        except Exception as e:
            logger.error(e.message)
            return None

    def __get_urls(self):
        url_pattern = re.compile('(https?://[.\d\w\./\?=&;\\%~]+)')
        urls = url_pattern.findall(self.msg)
        if not urls:
            raise ThirdMsgException('None of URL Exists In Msg.')
        for url in urls:
            if 'coupon' in url:
                self.cupon_url = url
            elif 'item.htm' in url:
                self.item_url = url
                self.item_source = WQMsg.item_sources.lanlan
            elif 's.click.taobao' in url:
                self.item_source = WQMsg.item_sources.other
                self.__get_301_urls(url)
        if self.item_url is None:
            raise NoItemException('Unable To Catch Item URL.')

    def __get_301_urls(self, url):
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0"
        cap["phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'
        self.driver = webdriver.PhantomJS(PHANTOMJS_PATH, desired_capabilities=cap)
        try:
            self.driver.get(url)
            self.cupon_url = self.driver.current_url
            # 这里需要activity_id使用sdk查询优惠券相关信息
            try:
                self.activity_id = re.findall('activityId=([\d\w]+)', self.cupon_url)[0]
            except IndexError:
                # raise ThirdMsgException('Unable To Parse Activity ID')
                self.activity_id = None
                self.__get_cupon_info_from_cupon_url()
            item_href = self.driver.find_element_by_class_name('item-detail')
            item_href.click()
            self.item_url = self.driver.current_url
        except Exception as e:
            logger.error(e)
        finally:
            self.driver.close()
            self.driver.quit()

    def __get_cupon_info_from_cupon_url(self):
        self.cupon_info = {
            "coupon_remain_count": 100,  # 此法暂不能获得剩余券数，先写死
            "coupon_amount": 0,
            "coupon_start_time": datetime.now().date().strftime('%Y-%m-%d'),  # 初始化为当前日期
            "coupon_end_time": (datetime.now() + timedelta(hours=4)).date().strftime('%Y-%m-%d'),  # 初始化有效期4小时
        }
        try:
            start_time, end_time = self.driver.find_element_by_class_name("coupons-data").text.split("-")
            start_time = start_time.replace('.', '-')
            end_time = end_time.replace('.', '-')
            coupon_amount = self.driver.find_element_by_class_name("coupons-price").text[1:]
            self.cupon_info.update({
                "coupon_amount": coupon_amount,
                "coupon_start_time": start_time,
                "coupon_end_time": end_time,
            })
        except Exception as e:
            logger.warning('Cupon Parsing Error: {}'.format(e))

    def __get_img(self):
        img_pattern = re.compile('\[CQ:image,file=(https?://[.\d\w\./\?=&;\\%~]+)\]')
        try:
            self.img_url = img_pattern.findall(self.msg)[0]
        except IndexError:
            self.img_url = None

    def __get_item_id(self):
        item_id_pattern = re.compile('item.htm\?id=(\d+)')
        try:
            self.item_id = item_id_pattern.findall(self.item_url)[0]
        except IndexError:
            raise NoItemException('Unable To Catch Item Id')

    def __fetch_detail(self):
        if self.item_source == WQMsg.item_sources.lanlan:
            resp = requests.get('http://www.lanlanlife.com/product/itemInfo?apiKey={0}&itemId={1}'.format(lanlan_apikey, self.item_id))
            if resp.status_code != 200 \
                    or resp.json()['status']['code'] != 1001 \
                    or resp.json()['result'] is None:
                raise ThirdMsgException('Unable To Fetch Detail From Lanlan.')
            else:
                self.product_dict = resp.json()['result']

        elif self.item_source == WQMsg.item_sources.other:
            item_info = get_item_info(self.item_id)

            # 若已在__get_cupon_info_from_cupon_url中获取过优惠券详情
            if hasattr(self, 'cupon_info'):
                cupon_info = self.cupon_info
            elif self.activity_id is not None:
                cupon_info = get_cupon_info(self.item_id, self.activity_id)
            else:
                cupon_info = None

            if item_info is None or cupon_info is None:
                raise ThirdMsgException('Unable To Fetch Item/Cupon Info With Item {}.'.format(self.item_id))
            self.product_dict = {
                # 按照下面的方法决定字段名
                # Product模型用
                "itemId": str(self.item_id),
                "shortTitle": item_info['title'],
                "desc": '',
                "coverImage": item_info['pict_url'],
                "couponMoney": cupon_info['coupon_amount'],
                "nowPrice": item_info['zk_final_price'],
                "couponUrl": self.cupon_url,
                "monthSales": item_info['volume'],
                "couponRemainCount": cupon_info['coupon_remain_count'],
                "couponStartTime": time.mktime(datetime.strptime(cupon_info['coupon_start_time'], '%Y-%m-%d').timetuple()),
                "couponEndTime": time.mktime(datetime.strptime(cupon_info['coupon_end_time'], '%Y-%m-%d').timetuple()),
                "tkRates": 0,
                "commision_amount": 0.0,
                "category": item_info['cat_name'],
                # ProductDetail模型用
                "sellerId": item_info['seller_id'],
                "sellerName": item_info['nick'],
                "auctionImages": item_info['small_images']['string'],
                "detailImages": self.__get_desc_imgs_from_mobile_api(),
                "item_url": self.item_url,
                "recommend": '',
            }

    def __get_desc_imgs_from_mobile_api(self):
        detail_url = 'http://hws.m.taobao.com/cache/wdetail/5.0/?id={}'.format(self.item_id)
        try:
            resp = requests.get(detail_url).json()
            desc_url = resp['data']['descInfo']['briefDescUrl']
            resp2 = requests.get(desc_url).json()
            desc_imgs = resp2['data']['images']
        except Exception as e:
            logger.warning('Unable To Fetch Desc Imgs Caused By Error {}.'.format(e))
            desc_imgs = []
        return desc_imgs

    def save_from_product_dict(self, item):
        product_dict = {
            'title': item['shortTitle'],
            'desc': '',
            'img_url': item['coverImage'].split('@')[
                           0] + '?x-oss-process=image/resize,w_600/format,jpg/quality,Q_80',
            'cupon_value': float(item['couponMoney'].strip()),
            'price': float(item['nowPrice']),
            'cupon_url': item['couponUrl'],
            'sold_qty': int(item['monthSales']),
            'cupon_left': item['couponRemainCount'],
            'commision_rate': str(item['tkRates']) + '%',
            'commision_amount': item['tkRates'] * float(item['nowPrice']) / 100,
            'cate': item['category']
        }
        # 若消息中有图片, 则替换原商品图
        if self.img_url is not None:
            product_dict['img_url'] = self.img_url + '?x-oss-process=image/resize,w_600/format,jpg/quality,Q_80'
        try:
            send_img = item['sendImage']
            img_size_str = re.findall('\_(\d+x\d+)\.', send_img)[0]
            img_size = img_size_str.split('x')
            img_scale = float(img_size[0]) / float(img_size[1])
            # 按照尺寸判断，尺寸在此范围内的认定为是直播秀的图，存库并发送用。
            if 100.0 / 80 < img_scale < 100.0 / 60:
                product_dict.update({'send_img': send_img})
        except:
            pass
        item_id = item['itemId']
        # if item['tkRates'] >= 20:
        p, created = Product.objects.update_or_create(item_id=item_id, defaults=product_dict)
        # else:
        #     raise  ThirdMsgException('Product {0} Got Low Commision Rate Of {1}.'.format(self.item_id, item['tkRates']/100.0))
        # if not datetime.fromtimestamp(
        #     float(item['couponStartTime'])) < datetime.now() < datetime.fromtimestamp(
        #     float(item['couponEndTime'])):
        #     p.available = False
        # p.refresh_from_db()
        # p.assert_available()
        update_productdetails(p, item)
        p.save()
        logger.info('Product Updated From Third Msg!')
        connection.close()


class MsgManager(object):
    """
    此类为针对多个消息来源，预留扩展空间而编写的类
    """
    sources = {
        'wanqun': WQMsg,
    }

    def __new__(cls, *args, **kwargs):
        """
        再此处传入source_key可以动态的决定使用哪个Msg类来进行构造和初始化，以返回不同类的实例。
        此处将返回__class类的实例，对实例访问属性将对应到__class类中
        对source_key的处理可以在C#代码中完成（因为酷Q插件中可以获取到完整的QQ消息的信息），
        也可以在本项目中完成， 但需在C#代码中传入更多信息。
        """
        source_key = kwargs.get('source_key', 'wanqun')
        __class = cls.sources[source_key]
        o = __class.__new__(__class)
        o.__init__(*args, **kwargs)
        return o


class ThirdMsgException(Exception):
    def __init__(self, msg):
        self.message = msg
        Exception.__init__(self, self.message)


class NoItemException(Exception):
    def __init__(self, msg):
        self.message = msg
        Exception.__init__(self, self.message)