# -*- coding: utf-8 -*-

from PIL import Image
from PIL import ImageFont, ImageDraw

import os
# import django
#
# os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
# django.setup()

import requests
import urllib2
from io import BytesIO
from broadcast.utils import OSSMgr
from django.core.cache import cache
from fuli.oss_utils import beary_chat

import uuid
import json
import time

import logging
logger = logging.getLogger("weixin_bot")

base_path = '/home/new_taobaoke/taobaoke/'
font_path = os.path.join(base_path, 'apps/broadcast/statics/poster/fonts/')

app_id = "wx82b7a0d64e85afd9"
app_secret = "d38bed17f6b53122007c94fe8be1b5f5"
token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'\
    .format(app_id, app_secret)

cache_key = 'wx_access_token'


def get_access_token():
    access_token = cache.get(cache_key)
    while not access_token:
        # requests库 Max retries exceeded解决方案
        token_response = requests.get(token_url, headers={'Connection': 'close'})
        access_token = json.loads(token_response.content).get("access_token", "")
        if access_token:
            cache.set(cache_key, access_token, 60*60)
            return access_token
        else:
            logger.error("获取access_token失败， 原因： {0}".format(json.loads(token_response.content)))
            beary_chat("获取access_token失败， 原因： {0}".format(json.loads(token_response.content)))
            # 5秒后重试
            time.sleep(5)
    return access_token


def retry_get_access_token():
    for _ in range(5):
        token_response = requests.get(token_url, headers={'Connection': 'close'})
        access_token = json.loads(token_response.content).get("access_token", "")
        if access_token:
            cache.set(cache_key, access_token, 60 * 60)
            return access_token
        else:
            logger.error("获取access_token失败， 原因： {0}".format(json.loads(token_response.content)))
            beary_chat("获取access_token失败， 原因： {0}".format(json.loads(token_response.content)))


def generate_qrcode(req_data):
    """
    req_data = {
        "page": "pages/xx/xx",
        "scene": "{0}${1}".format(xx, xx)
    }
    """
    # 根据url生成二维码, 返回二维码的url
    access_token = get_access_token()
    logger.info("access_token: {}".format(access_token))
    qr_url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}'.format(access_token)

    # 这里得到的二维码的字节流
    qrcode_response = requests.post(qr_url, data=json.dumps(req_data), headers={'Connection': 'close'})

    try:
        res_dict = json.loads(qrcode_response.content)
        errcode = res_dict.get("errcode", "")
        if errcode:
            logger.info("重新获取access_token")
            access_token = retry_get_access_token()
            qr_url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}'.format(access_token)
            qrcode_response = requests.post(qr_url, data=json.dumps(req_data), headers={'Connection': 'close'})
            return qrcode_response.content
        else:
            return qrcode_response.content
    except Exception as e:
        return qrcode_response.content


def generate_image(product_url_list, qrcode_flow,price_list):

    # 首先调用二维码生成函数
    extra = 0
    if len(product_url_list) == 3:
        extra = 300

    # 新建画布
    toImage = Image.new('RGBA', (600, 800+extra))

    # 获取商品主图
    product_data = urllib2.urlopen(product_url_list[0]).read()
    product_img = Image.open(BytesIO(product_data))
    product_size = product_img.resize((600, 600))
    product_location = (0, 0)
    toImage.paste(product_size, product_location)

    if len(product_url_list) == 3:
        # 获取300*300图1
        product_1_data = urllib2.urlopen(product_url_list[1]).read()
        product_1_img = Image.open(BytesIO(product_1_data))
        product_1_size = product_1_img.resize((300, 300))
        product_1_location = (0, 600)
        toImage.paste(product_1_size, product_1_location)

        # 获取300*300图2
        product_2_data = urllib2.urlopen(product_url_list[2]).read()
        product_2_img = Image.open(BytesIO(product_2_data))
        product_2_size = product_2_img.resize((300, 300))
        product_2_location = (300, 600)
        toImage.paste(product_2_size, product_2_location)

    if len(price_list) == 2:
        # 填充券前券后价格
        price_img = image_update(price_list)
        price_location = (200, 600 + extra)
        toImage.paste(price_img, price_location)

        # 获取二维码
        qrcode_bytes = qrcode_flow
        qrcode_img = Image.open(BytesIO(qrcode_bytes))
        qrcode_size = qrcode_wrap(qrcode_img)
        qrcode_location = (0, 600 + extra)
        toImage.paste(qrcode_size, qrcode_location)

    else:
        # 获取长按扫描图# 将图片进行拼接
        BASE_DIR = os.getcwd()
        saomiao_img = Image.open(os.path.join(BASE_DIR, 'apps/broadcast/utils/lingqu.jpg'))
        saomiao_size = saomiao_img.resize((400, 200))
        saomiao_location = (200, 600 + extra)
        toImage.paste(saomiao_size, saomiao_location)

        # 获取二维码
        qrcode_bytes = qrcode_flow
        qrcode_img = Image.open(BytesIO(qrcode_bytes))
        qrcode_size = qrcode_img.resize((200, 200))
        qrcode_location = (0, 600 + extra)
        toImage.paste(qrcode_size, qrcode_location)

    new_image = toImage.convert("RGBA").tobytes("jpeg", "RGBA")
    filename = '{}.jpeg'.format(uuid.uuid1())
    # 将图片进行拼接
    print(toImage.size)
    oss = OSSMgr()
    oss.bucket.put_object(filename, new_image)

    # 压缩率为65
    print 'http://md-oss.di25.cn/{}?x-oss-process=image/quality,q_65'.format(filename)
    return 'http://md-oss.di25.cn/{}?x-oss-process=image/quality,q_65'.format(filename)

def image_update(price_list):
    image = Image.new('RGB', (400, 200), (255, 255, 255))
    truetype = os.path.join(font_path, 'ya.ttc')
    font1 = ImageFont.truetype(truetype, 32)
    font2 = ImageFont.truetype(truetype, 64)
    redColor = "#ff0000"
    blackColor = "#000000"
    whiteColor = '#ffffff'
    draw = ImageDraw.Draw(image)
    draw.rectangle([(20, 100), (100, 150)], fill=redColor)
    draw.text((20, 40), u'现价:￥' + str(price_list[0]), font=font1, fill=blackColor)
    draw.text((20, 100), u'券后:', font=font1, fill=whiteColor)
    draw.text((100, 80), u'￥' + str(price_list[1]), font=font2, fill=redColor)
    draw.line([(100, 63), (180 + (len(str(price_list[0])) - 3) * 15, 63)], fill=blackColor, width=3)
    return image

def qrcode_wrap(qrcode_img):
    redColor = "#ff0000"
    blackColor = "#000000"
    Im = Image.new('RGB',(200,200),(255,255,255))
    Im.paste(qrcode_img.resize((160, 160)),(18,13))
    draw = ImageDraw.Draw(Im)
    truetype = os.path.join(font_path, 'ya.ttc')
    font =ImageFont.truetype(font=truetype,size=16)
    draw.text((32,173),u'长按识别小程序码',font=font,fill=blackColor)
    draw.line([(15,10),(35,10)],fill=redColor,width=2)
    draw.line([(15,10),(15,30)],fill=redColor,width=2)

    draw.line([(15,170),(35,170)],fill=redColor,width=2)
    draw.line([(15,170),(15,150)],fill=redColor,width=2)

    draw.line([(185,10),(165,10)],fill=redColor,width=2)
    draw.line([(185,10),(185,30)],fill=redColor,width=2)

    draw.line([(185,170),(165,170)],fill=redColor,width=2)
    draw.line([(185,170),(185,150)],fill=redColor,width=2)
    return Im
if __name__ == '__main__':
    product_url = "http://oss3.lanlanlife.com/eed86f7a8731d12c3a8173cff019a309_800x800.jpg?x-oss-process=image/resize,w_600/format,jpg/quality,Q_80"
    # product_url_list = [product_url, product_url, product_url]
    # qrcode_flow = generate_qrcode(1006013, "heihei")
    # generate_image(product_url_list, qrcode_flow)
