# -*- coding: utf-8 -*-
import hashlib
import random
import string
import time

MCH_KEY = "1c1b0d3e23eb4a88f54bcdih155wvndkjn545"


def get_sign_str(appid, mch_id, device_info="maxwell", body="maxwell"):
    string = "appid={appid}&body={body}&device_info={device_info}&mch_id={mch_id}".\
        format(appid=appid, body=body, device_info=device_info, mch_id=mch_id)
    string_sign_temp = string + "&key=".format(MCH_KEY)
    sign = hashlib.md5(string_sign_temp).hexdigest()
    return sign


def get_random_str():
    random_string = ''.join(random.sample(string.ascii_letters + string.digits, 32))
    return random_string


def get_trade_num(item_id):
    """
    获取商户内部商品订单号
    """
    # 10位时间戳
    timestamp = str(int(time.time()))
    trade_num = timestamp + item_id
    return trade_num

