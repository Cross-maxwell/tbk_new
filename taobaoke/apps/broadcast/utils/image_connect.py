# -*- coding: utf-8 -*-

from PIL import Image
from PIL import ImageFont, ImageDraw, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

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
# base_path = '/home/adam/mydev/projects/new_sys/taobaoke/'
# base_path = '/home/smartkeyerror/PycharmProjects/new_taobaoke/taobaoke'
font_path = os.path.join(base_path, 'apps/broadcast/statics/poster/fonts/')

app_id = "wx82b7a0d64e85afd9"
app_secret = "d38bed17f6b53122007c94fe8be1b5f5"
token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}' \
    .format(app_id, app_secret)

cache_key = 'wx_access_token'


def get_access_token():
    access_token = cache.get(cache_key)
    while not access_token:
        # requests库 Max retries exceeded解决方案
        token_response = requests.get(token_url, headers={'Connection': 'close'})
        access_token = json.loads(token_response.content).get("access_token", "")
        if access_token:
            cache.set(cache_key, access_token, 60 * 60)
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


def generate_image(product_url_list, qrcode_flow, price_list, title=''):
    # 首先调用二维码生成函数
    extra = 0
    if len(product_url_list) == 3:
        extra = 300

    # 新建画布
    toImage = Image.new('RGBA', (600, 800 + extra))

    # 获取商品主图
    try:
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

        if len(price_list) == 3:
            # 填充券前券后价格
            price_img = image_update(price_list, title)
            price_location = (0, 600 + extra)
            toImage.paste(price_img, price_location)

            # 获取二维码
            qrcode_bytes = qrcode_flow
            qrcode_img = Image.open(BytesIO(qrcode_bytes))
            qrcode_size = qrcode_wrap(qrcode_img)
            qrcode_location = (400, 600 + extra)
            toImage.paste(qrcode_size, qrcode_location)

        else:
            # 获取长按扫描图# 将图片进行拼接
            BASE_DIR = os.getcwd()
            saomiao_img = Image.open(os.path.join(BASE_DIR, 'apps/broadcast/utils/lingqu.jpg'))
            saomiao_size = saomiao_img.resize((400, 200))
            saomiao_location = (0, 600 + extra)
            toImage.paste(saomiao_size, saomiao_location)

            # 获取二维码
            qrcode_bytes = qrcode_flow
            qrcode_img = Image.open(BytesIO(qrcode_bytes))
            qrcode_size = qrcode_img.resize((200, 200))
            qrcode_location = (400, 600 + extra)
            toImage.paste(qrcode_size, qrcode_location)
    except Exception as e:
        logger.error(e)

    new_image = toImage.convert("RGBA").tobytes("jpeg", "RGBA")
    filename = '{}.jpeg'.format(uuid.uuid1())
    # 将图片进行拼接
    print(toImage.size)
    oss = OSSMgr()
    oss.bucket.put_object(filename, new_image)

    # 压缩率为65
    print 'http://md-oss.di25.cn/{}?x-oss-process=image/quality,q_50'.format(filename)
    return 'http://md-oss.di25.cn/{}?x-oss-process=image/quality,q_50'.format(filename)


def image_update(price_list, title):
    image = Image.new('RGB', (400, 200), (255, 255, 255))
    truetype = os.path.join(font_path, 'hei.ttf')
    font = ImageFont.truetype(truetype, 23)
    font1 = ImageFont.truetype(truetype, 20)
    font2 = ImageFont.truetype(truetype, 40)
    redColor = "#ff0000"
    blackColor = "#000000"
    whiteColor = '#ffffff'
    gray = "#808080"
    # orange = "#FF8C00"
    orange = "#FF6347"
    title_wrap = '\n'.join(title[i:i + 15] for i in range(0, len(title), 15))

    draw = ImageDraw.Draw(image)
    draw.multiline_text((20, 0), title_wrap, font=font, fill=blackColor, align='left', spacing=5)
    # draw.rectangle([(5, 118), (90, 170)], fill=redColor)
    draw.text((130, 150), u'券后价:', font=font1, fill=gray)
    draw.text((200, 150), u'￥', font=font1, fill=orange)
    draw.text((220, 130), str(price_list[1]), font=font2, fill=orange)
    draw.text((20, 110), u'销售价:￥' + str(price_list[0]), font=font1, fill=gray)
    # draw.line([(10, 155), (130 + (len(str(price_list[0])) - 3) * 15, 155)], fill=blackColor, width=3)
    quan_img(image)
    draw.text((56, 147), str(int(price_list[2]))+u'元', font=font1, fill=orange)
    return image


def quan_img(org_img):
    BASE_DIR = os.getcwd()
    org_quan_img = Image.open(os.path.join(BASE_DIR, 'apps/broadcast/utils/quan.png'))
    saomiao_size = org_quan_img.resize((100, 35))
    org_img.paste(saomiao_size, (20, 145))


def qrcode_wrap(qrcode_img):
    redColor = "#ff0000"
    blackColor = "#000000"
    Im = Image.new('RGB', (200, 200), (255, 255, 255))
    Im.paste(qrcode_img.resize((160, 160)), (18, 13))
    draw = ImageDraw.Draw(Im)
    truetype = os.path.join(font_path, 'hei.ttf')
    font = ImageFont.truetype(font=truetype, size=16)
    draw.text((32, 173), u'长按识别小程序码', font=font, fill=blackColor)
    draw.line([(15, 10), (35, 10)], fill=redColor, width=2)
    draw.line([(15, 10), (15, 30)], fill=redColor, width=2)

    draw.line([(15, 170), (35, 170)], fill=redColor, width=2)
    draw.line([(15, 170), (15, 150)], fill=redColor, width=2)

    draw.line([(185, 10), (165, 10)], fill=redColor, width=2)
    draw.line([(185, 10), (185, 30)], fill=redColor, width=2)

    draw.line([(185, 170), (165, 170)], fill=redColor, width=2)
    draw.line([(185, 170), (185, 150)], fill=redColor, width=2)
    return Im


if __name__ == '__main__':
    product_url = "http://oss1.lanlanlife.com/5b485f3ba40bdfd97507cdc6da24ad25_800x800.jpg?x-oss-process=image/resize,w_600/format,jpg/quality,Q_80"
    # product_url_list = [product_url]
    # req_data = {
    #     "page": "pages/goods/goods",
    #     "scene": "{0}${1}${2}".format("68263", "￥Tjcf0RcyHYS￥", "2369")
    # }
    # # qrcode_flow = generate_qrcode(req_data)
    # price_list = [round(100.00, 2), round(80.00, 2), round(20.00, 2)]
    # title = u'竹炭超级柔软牙刷，你值得拥有！！！超级无敌好用，差点就不想卖了'.encode('utf-8')
    # generate_image(product_url_list, bytes("1"), price_list, title)