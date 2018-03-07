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

    场景：
    A. 消息形式：
            [CQ:img file=http://some.img.url]
            纯棉品质，卡通图案！
            可爱有活力，多颜色可选！
            【一米半糖】儿童开衫外套
            【原价69元】券后【39元】
            领券：http://shop.m.taobao.com/shop/coupon.htm?seller_id=1135287324&activity_id=0526b688e7b24194a338576e6b4c94a6
            抢购：https://detail.tmall.com/item.htm?id=563557952476

        标准商品链接，直达淘宝详情页，可从中取出item_id

    B. 消息形式：
            [CQ:img file=http://some.img.url]
            无糖粗粮曲奇饼干268g*2袋
            19.89
            9.89
            https://s.click.taobao.com/HcBXgTw

        二合一短链，需使用phantomjs进入短链，获取item_id和activity_id

    调用parse方法的Process:
    0. 从消息中获取url，
        0.1 消息中没有链接， 即无图片、无链接的纯文字消息。
    1. 根据链接内容确定url类型，是否领券链接及商品链接。
        1.1 找到商品链接，确定来源为懒懒，对应场景A
            1.1.1 从消息中获取商品图片
                1.1.1.1 从商品链接中获取商品id，
                    1.1.1.1.1 从懒懒的接口获取到详情，包括商品详情和优惠券详情，赋值给self.product_dict
                        1.1.1.1.1.1 使用self.product_dict，将商品存库
                            final 最终返回item_id
                    1.1.1.1.2 懒懒未查询到此商品，抛出ThirdMsgException
                1.1.1.2 未能获取到商品id， 抛出NoItemException
        1.2 未找到商品链接，抛出NoItemException
        1.3 s.click.taobao形式的短链，确定为其他来源，对应场景B
            1.3.1 打开短链，获取coupon_url
                1.3.1.1 从coupon_url 中获取activity_id（用于后续使用淘宝sdk获取优惠券详情）
                1.3.1.2 未获取到activity_id, 从优惠券页面解析到优惠券详情， 并赋值到self.cupon_info
                    1.3.1.1.1 进入商品详情页，获取商品链接
                        1.1.1 从消息中获取商品图片
                            1.1.1.1 从商品链接中获取商品id
                                1.3.1.1.1.1 使用淘宝sdk分别获取商品详情（使用item_id），优惠券详情（若有，使用activity_id），拼接成self.product_dict
                                    1.1.1.1.1.1 使用self.product_dict，将商品存库
                                        final 最终返回item_id
                            1.1.1.2 未能获取到商品id， 抛出NoItemException
    """

    # 使用此枚举类用以维护商品来源
    item_sources = Enum('item_source', ('lanlan', 'other'))

    def __init__(self, msg):
        # 调用基类构造方法，将msg绑定到实例属性
        super(WQMsg, self).__init__(msg)
        self.item_url = None
        self.img_url = None
        self.item_id = None
        self.item_source = None
        self.product_dict = None

    def reorganize(self):
        """
        若未解析到商品，调用此方法，将消息重组并返回由图片url和文本组成的列表
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
        img_url_pattern = re.compile('\[CQ:image,file=(.*?)\]')
        try:
            img_url = img_url_pattern.findall(self.msg)[0]
        except IndexError:
            img_url = None
        except Exception as e:
            logger.error(e)
            img_url = None
        finally:
            CQ_pattern = re.compile('(\[CQ:.*?\])')
            self.msg = CQ_pattern.sub('', self.msg)
            return img_url

    def parse(self):
        """
        解析商品并存库
        :return: 解析成功返回item_id, 解析失败返回None, 或者抛出NoItemException错误
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
            logger.error(e)
            return None

    def __get_urls(self):
        # process 0
        url_pattern = re.compile('(https?://[.\d\w\./\?=&;\\%~]+)')
        urls = url_pattern.findall(self.msg)
        if not urls:
            # process 0.1
            raise ThirdMsgException('None of URL Exists In Msg.')
        for url in urls:
            # process 1
            if 'coupon' in url:
                self.cupon_url = url
            elif 'item.htm' in url:
                # process 1.1
                self.item_url = url
                self.item_source = WQMsg.item_sources.lanlan
            elif 's.click.taobao' in url:
                # process 1.3
                self.item_source = WQMsg.item_sources.other
                self.__get_301_urls(url)
        if self.item_url is None:
            # process 1.2
            raise NoItemException('Unable To Catch Item URL.')

    def __get_301_urls(self, url):
        # cap = webdriver.DesiredCapabilities.PHANTOMJS
        # cap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0"
        # cap["phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'
        # self.driver = webdriver.PhantomJS(PHANTOMJS_PATH, desired_capabilities=cap)
        self.driver = webdriver.Chrome('./chromedriver')
        try:
            # process 1.3.1
            self.driver.get(url)

            if 'activityId' in self.driver.current_url:
                self.cupon_url = self.driver.current_url
                # 这里需要activity_id使用sdk查询优惠券相关信息
                try:
                    # process 1.3.1.1
                    self.activity_id = re.findall('activityId=([\d\w]+)', self.cupon_url)[0]
                except IndexError:
                    # raise ThirdMsgException('Unable To Parse Activity ID')
                    # process 1.3.1.2
                    self.activity_id = None
                    self.__get_cupon_info_from_cupon_url()
                # process 1.3.1.1.1
                item_href = self.driver.find_element_by_class_name('item-detail')
                item_href.click()
                self.item_url = self.driver.current_url
            elif 'item.htm' in self.driver.current_url:
                self.item_url = self.driver.current_url
                self.item_source = WQMsg.item_sources.lanlan
            elif 'edetail?' in self.driver.current_url:
                self.driver.find_element_by_css_selector('.item-detail-view a').click()
                self.item_url = self.driver.current_url
                self.item_source = WQMsg.item_sources.lanlan
        except Exception as e:
            logger.error(e)
        finally:
            self.driver.close()
            self.driver.quit()

    def __get_cupon_info_from_cupon_url(self):
        # process 1.3.1.2
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
        # p 1.1.1
        img_pattern = re.compile('\[CQ:image,file=(https?://[.\d\w\./\?=&;\\%~]+)\]')
        try:
            self.img_url = img_pattern.findall(self.msg)[0]
        except IndexError:
            self.img_url = None

    def __get_item_id(self):
        # p 1.1.1.1
        item_id_pattern = re.compile('item.htm\?.*?id=(\d+)')
        try:
            self.item_id = item_id_pattern.findall(self.item_url)[0]
        except IndexError:
            # p 1.1.1.2
            raise NoItemException('Unable To Catch Item Id')

    def __fetch_detail(self):
        if self.item_source == WQMsg.item_sources.lanlan:
            resp = requests.get('http://www.lanlanlife.com/product/itemInfo?apiKey={0}&itemId={1}'.format(lanlan_apikey, self.item_id))
            if resp.status_code != 200 \
                    or resp.json()['status']['code'] != 1001 \
                    or resp.json()['result'] is None:
                # p 1.1.1.1.2
                raise ThirdMsgException('Unable To Fetch Detail From Lanlan.')
            else:
                # p 1.1.1.1.1
                self.product_dict = resp.json()['result']

        elif self.item_source == WQMsg.item_sources.other:
            # process 1.3.1.1.1.1
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
        # p 1.1.1.1.1.1
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