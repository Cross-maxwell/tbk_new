# -*- coding: utf-8 -*-
import hashlib
import random
import string
import time

MCH_KEY = "1c1b0d3e23eb4a88f54bcdih155wvndkjn545"

KEY = "2739d39befe4064e6c8a8ee09d48102d"


"""
stringA="appid=wxd930ea5d5a258f4f&body=test&device_info=1000&mch_id=10000100&nonce_str=ibuaiVcKdpRxkhJA";

         appid=wxb2e3e953b7f9c832&body=测试&device_info=1000&mch_id=1481668232&nonce_str=juIQicwzH9Ot3EBD&key=2739d39befe4064e6c8a8ee09d48102d
"""


def get_sign_str(sorted_dict):
    """
    接受dict
    """
    stringA = ""
    for key, value in sorted_dict:
        stringA += key + "=" + str(value) + "&"
    print stringA
    string_sign_temp = stringA + "key=" + KEY
    print string_sign_temp
    sign = hashlib.md5(string_sign_temp).hexdigest()
    return sign.upper()


def get_random_str():
    random_string = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    return random_string


def get_trade_num(item_id):
    """
    获取商户内部商品订单号
    """
    # 10位时间戳
    timestamp = str(int(time.time()))
    trade_num = timestamp + item_id
    return trade_num

