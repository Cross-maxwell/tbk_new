# -*- coding: utf-8 -*-
import hashlib
import random
import string
import time
import requests
from bs4 import BeautifulSoup

MCH_KEY = "1c1b0d3e23eb4a88f54bcdih155wvndkjn545"

KEY = "2739d39befe4064e6c8a8ee09d48102d"


"""
stringA="appid=wxd930ea5d5a258f4f&body=test&device_info=1000&mch_id=10000100&nonce_str=ibuaiVcKdpRxkhJA";

appId=&nonceStr&package=prepay_id=wx2017033010242291fcfe0db70013231072&signType=MD5&timeStamp=1490840662&key=qazwsxedcrfvtgbyhnujmikolp111111
appId=&nonceStr&package=prepay_id=wx201712281528146c38287b210933847072&signType=MD5&timeStamp=1514446096&key=2739d39befe4064e6c8a8ee09d48102d

appId=&nonceStr&package=prepay_id=wx20180106115440fa23973aaf0716631912&signType=MD5&timeStamp=1515210893&'
"""


def get_sign_str(sorted_dict):
    """
    接受dict
    """
    stringA = ""
    for key, value in sorted_dict:
        stringA += key + "=" + str(value) + "&"
    string_sign_temp = stringA + "key=" + KEY
    sign = hashlib.md5(string_sign_temp).hexdigest()
    print string_sign_temp
    return sign.upper()


def get_random_str():
    random_string = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    return random_string


def get_8_random_str():
    random_string = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    return random_string


def get_64_random_number_string():
    random_seeds = "123456789"
    random_list = []
    for i in range(64):
        random_list.append(random.choice(random_seeds))
    return "".join(random_list)


def get_trade_num(item_id):
    """
    获取商户内部商品订单号
    """
    # 10位时间戳
    timestamp = str(int(time.time()))
    random_str = get_8_random_str()
    trade_num = timestamp + item_id + random_str
    return trade_num


def trans_dict_to_xml(data):
    """
    将dict对象转换成微信支付交互所需的XML格式数据
    """
    xml = []
    for k in sorted(data.keys()):
        v = data.get(k)
        if k == 'detail' and not v.startswith('<![CDATA['):
            v = '<![CDATA[{}]]>'.format(v)
        xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    fin_xml = '<xml>{}</xml>'.format(''.join(xml))
    return fin_xml


def trans_xml_to_dict(xml):
    """
    将微信支付交互返回的XML格式数据转化为Dict对象
    """
    soup = BeautifulSoup(xml, features='xml')
    xml = soup.find('xml')

    # 将 XML 数据转化为 Dict
    data = dict([(item.name, item.text) for item in xml.find_all()])
    return data


def beary_chat(text, user=None):
    requests.post(
        "https://hook.bearychat.com/=bw8Zi/incoming/Nd082nGFy60ZZl1NggGBPj3kpwo0TFuur4HLVqAUPrY=",
        json={
            "user": user,
            "text": text
        }
    )




# req_xml_data = """
# <xml>
#    <appid>{appid}</appid>
#    <attach>{attach}</attach>
#    <body>{body}</body>
#    <mch_id>{mch_id}</mch_id>
#    <nonce_str>{nonce_str}</nonce_str>
#    <notify_url>{notify_url}</notify_url>
#    <openid>{openid}</openid>
#    <out_trade_no>{out_trade_no}</out_trade_no>
#    <spbill_create_ip>{spbill_create_ip}</spbill_create_ip>
#    <total_fee>{total_fee}</total_fee>
#    <trade_type>JSAPI</trade_type>
#    <sign>{sign}</sign>
# </xml>
# """.format(appid=appid, attach=attach, body=body, mch_id=mch_id, nonce_str=nonce_str, notify_url=notify_url,
#            openid=openid, out_trade_no=out_trade_no, spbill_create_ip=spbill_create_ip, total_fee=total_fee,
#           sign=sign)
# print req_xml_data

