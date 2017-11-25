# -*- coding: utf-8 -*-

from PIL import Image
import os
import requests
import urllib2
from io import BytesIO
from broadcast.utils import OSSMgr
import uuid
import json

import logging
logger = logging.getLogger("weixin_bot")



def generate_qrcode(product_id, tkl):
    # 根据url生成二维码, 返回二维码的url
    app_id = "wx82b7a0d64e85afd9"
    app_secret = "d38bed17f6b53122007c94fe8be1b5f5"
    token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'\
        .format(app_id, app_secret)

    token_response = requests.get(token_url)
    access_token = json.loads(token_response.content).get("access_token", "")
    if not access_token:
        logger.error("获取access_token失败")
    qr_url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}'.format(access_token)
    req_data = {
        "page": "pages/goods/goods",
        "scene": "{0}${1}".format(product_id, tkl)
    }
    # 这里得到的二维码的字节流
    qrcode_response = requests.post(qr_url, data=json.dumps(req_data))

    return qrcode_response.content


def generate_image(product_id, tkl, product_url):

    # 首先调用二维码生成函数

    # 新建画布
    toImage = Image.new('RGBA', (600, 800))

    # 获取二维码
    logger.info("product_id: {0}, tkl: {1}, product_url: {2}".format(product_id, tkl, product_url))
    qrcode_bytes = generate_qrcode(product_id, tkl)
    qrcode_img = Image.open(BytesIO(qrcode_bytes))
    qrcode_size = qrcode_img.resize((200, 200))
    qrcode_location = (0, 600)
    toImage.paste(qrcode_size, qrcode_location)

    # 获取商品主图
    product_data = urllib2.urlopen(product_url).read()
    product_img = Image.open(BytesIO(product_data))
    product_size = product_img.resize((600, 600))
    product_location = (0, 0)
    toImage.paste(product_size, product_location)

    # 获取长按扫描图# 将图片进行拼接
    BASE_DIR = os.getcwd()
    saomiao_img = Image.open(os.path.join(BASE_DIR, 'apps/broadcast/utils/lingqu.jpg'))
    saomiao_size = saomiao_img.resize((400, 200))
    saomiao_location = (200, 600)
    toImage.paste(saomiao_size, saomiao_location)
    new_image = toImage.convert("RGBA").tobytes("jpeg", "RGBA")

    filename = '{}.jpeg'.format(uuid.uuid1())
    # 将图片进行拼接
    print(toImage.size)
    oss = OSSMgr()
    oss.bucket.put_object(filename, new_image)
    print 'http://md-oss.di25.cn/{}'.format(filename)
    return 'http://md-oss.di25.cn/{}'.format(filename)


if __name__ == '__main__':
    generate_image(1006013, "heihei", "http://oss3.lanlanlife.com/eed86f7a8731d12c3a8173cff019a309_800x800.jpg?x-oss-process=image/resize,w_600/format,jpg/quality,Q_80")