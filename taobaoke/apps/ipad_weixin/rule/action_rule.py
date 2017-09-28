# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

import json
import requests
from django.utils.encoding import iri_to_uri

from ipad_weixin.models import Contact, Qrcode
from broadcast.models.user_models import TkUser
from broadcast.views.server_settings import S_PROD_07_INT


def filter_keyword_rule(wx_id, msg_dict):
    # http://s-prod-04.qunzhu666.com:8000/search-product-pad?username=15900000010&keyword=鞋子&gid=7682741189@chatroom
    # http://s-prod-04.qunzhu666.com:8000/interact/search-product-pad/?username=wxid_3cimlsancyfg22&keyword=%E9%9E%8B%E5%AD%90&gid=6362478985@chatroom
    # 条件1 文字符合要求
    keyword = find_buy_start(msg_dict['Content'])
    if keyword and keyword is not '':
        # FromUserName 跟 ToUserName 是相对机器人来说的
        # 机器人在群里说话，FromUserName是机器人的wx_id，ToUserName是gid
        # 但其他人在群里说话，ToUserName是机器人的wx_id，FromUserName是gid
        # 群是淘宝客群，找XX才生效
        is_taobao_group = False
        gid = ''
        # 情况分类1 机器人自己说找XX
        if msg_dict['FromUserName'] == wx_id and "@chatroom" in msg_dict['ToUserName']:
            gid = msg_dict['ToUserName']
            is_taobao_group = True
        # 情况分类2 群成员说找XX
        elif "@chatroom" in msg_dict['FromUserName'] and msg_dict['ToUserName'] == wx_id:
            gid = msg_dict['FromUserName']
            is_taobao_group = True
        # gid名称是福利社
            """
            为什么是first?
            """
            contact_db = Contact.objects.filter(nickname__contains="福利社",
                                                username=gid).first()
        gid_name_is = contact_db is not None
        if is_taobao_group and gid_name_is:
            # 根据id找到username
                qrcode_db = Qrcode.objects.filter(username=wx_id).first()
                username = qrcode_db.md_username

                uin = wx_id
                key_word = keyword
                if username == '' or key_word == '' or gid == '' or uin == '':
                    print ("incorrect params,username:{0},keyword:{1}, gid:{2}".format(username, key_word, gid))

                """
                发送给BotService，处理函数位于tbk>views>tbk_agent_views.py
                """
                r = requests.get("http://" + S_PROD_07_INT + "/api/tk/check-search?username={0}".format(username),
                                 timeout=10)
                if r.status_code != 200:
                    return ("remote server ret_code:{0} --{1}".format(r.status_code, r.text))
                ret_code = json.loads(json.loads(r.text))

                if ret_code['data'] != 1:
                    return ("check search fail:{0}".format(ret_code['data']))

                tku = TkUser.objects.get(user__username=username)
                text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
                    {}""".format(iri_to_uri(tku.get_search_url(key_word)))

                params_dict = {
                    "uin": uin,
                    "group_id": gid,
                    "text": text,
                    "type": "text"
                }

                from ipad_weixin.send_msg_type import send_msg_type

                send_msg_type(params_dict)
                print "Push text %s to group %s." % (params_dict['text'], params_dict['group_id'])




def find_buy_start(s):
    # 一个中文字符等于三个字节 允许有十个字符
    if len(s) < 40:
        lst = s.split("找")
        if len(lst) > 1:
            return lst[1]
        lst = s.split("买")
        if len(lst) > 1:
            return lst[1]
    return False


if __name__ == "__main__":
    print(find_buy_start("我要找拖鞋找拖鞋1"))
    print(find_buy_start("我要找拖鞋"))
    print(find_buy_start("我要买拖鞋"))
