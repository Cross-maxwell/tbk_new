# -*- coding: utf-8 -*-
"""
淘宝客推送脚本, 向已经激活的、带有“福利社”的群组推送从lanlanlife取得的商品。post_taobaoke_url测试正常
部署在s-proc-04 supervisor上，可直接访问 s-prod-04.qunzhu666.com:9001 (admin/123456)

"""
import sys
# 脚本加入搜索路径 现在是hard code状态 看看有没有办法改
sys.path.append('/Users/hong/sourcecode/work/ipad_wechat_test/wx_pad_taobaoke')
sys.path.append('/home/ipad_wechat_test/wx_pad_taobaoke')
# print(sys.path)

import json
import time
import datetime
import random
import requests

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from django.db.models import Q
from django.utils import timezone

from ipad_weixin.models import Qrcode, Message, WxUser, Contact
from ipad_weixin.send_msg_type import send_msg_type
from broadcast.models.user_models import TkUser
from broadcast.models.entry_models import Product, PushRecord

import logging
logger = logging.getLogger('post_taobaoke')


def post_taobaoke_url(wx_id, group_id, md_username):
    # 发单人的wx_id, 群的id, 手机号
    try:
        tk_user = TkUser.get_user(md_username)
    except Exception as e:
        logger.error(e)

    pid = tk_user.adzone.pid

    qs = Product.objects.filter(
        ~Q(pushrecord__group__contains=group_id,
           pushrecord__create_time__gt=timezone.now() - datetime.timedelta(days=3)),
        available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=1000),
    )

    # 用发送过的随机商品替代
    if qs.count() == 0:
        qs = Product.objects.filter(
            available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=1000),
        )
        requests.post(
            'https://hook.bearychat.com/=bw8NI/incoming/219689cd1075dbb9b848e4c763d88de0',
            json={'text': '点金推送商品失败：无可用商品, group_id=%s' % group_id}
        )

    for _ in range(50):
        try:
            r = random.randint(0, qs.count() - 1)
            p = qs.all()[r]
            break
        except Exception as exc:
            print "Get entry exception. Count=%d." % qs.count()
            logger.error(exc)
            print exc.message

    # img or text
    text_msg_dict = {
        #群主 id
        "uin": wx_id,
        #群/联系人 id
        "group_id": group_id,
        "text": p.get_text_msg(pid=pid),
        "type": "text",
        #这里 delay_time = 40, 能够刚好让200K左右的图片先发出， 文字信息紧随其后
        "delay_time": 40
    }


    img_msg_dict = {
        "uin": wx_id,
        "group_id": group_id,
        "text": p.get_img_msg(),
        "type": "img"
    }

    # TODO: 当程序的休眠时间为30分钟时，发送图片和文字的间隔为45分钟。当打印完 push ... to .. 之后，15分钟后才开始进行图片的额发送。why?




    PushRecord.objects.create(entry=p, group=group_id)
    send_msg_type(img_msg_dict)
    logger.info("Push img %s to group %s." % (img_msg_dict['text'], img_msg_dict['group_id']))

    # print "%s Push img %s to group %s." % (datetime.datetime.now(), img_msg_dict['text'], img_msg_dict['group_id'])
    send_msg_type(text_msg_dict)
    logger.info("Push text %s to group %s." % (img_msg_dict['text'], img_msg_dict['group_id']))

    # print "%s Push text %s to group %s." % (datetime.datetime.now(), text_msg_dict['text'], text_msg_dict['group_id'])


def select():
    # 筛选出已经登录的User
    user_list = WxUser.objects.filter(login__gt = 0).all()
    print([user.username for user in user_list])
    for user in user_list:
        print("handling wxid {}".format(user.username))
        # 发单机器人id
        wx_id = user.username
        # 通过 wx_id = hid 筛选出手机号
        qr_code_db = Qrcode.objects.filter(username=user.username).all()
        for qr_code in qr_code_db:
            if qr_code.md_username is not None:
                md_username = qr_code.md_username
                break
        rsp = requests.get("http://s-prod-07.qunzhu666.com:8000/api/tk/is-push?username={0}&wx_id={1}".format(md_username, wx_id), timeout=4)
        ret = json.loads(rsp.text)['ret']
        if ret == 1:
            # 筛选出激活群
            message_list = Message.objects.filter(content__contains="激活",
                                                  from_username=user.username).all()
            group_set = set([message.to_username for message in message_list])
            for group_id in group_set:
                # 发单人的wx_id, 群的id, 手机号
                try:
                    contact_db = Contact.objects.filter(nickname__contains="福利社",
                                                        username=group_id).first()
                    if contact_db is not None:
                        print(contact_db.nickname)
                        post_taobaoke_url(wx_id, group_id, md_username)
                except Exception as e:
                    logging.error(e)
                    print(e)

if __name__ == "__main__":
    # while True:
    #     user_list = WxUser.objects.filter(login__gt = 0).all()
    #     user_len = len([user.username for user in user_list])
    #     try:
    #         now_hour = int(time.strftime('%H', time.localtime(time.time())))
    #         if 7 <= now_hour <= 22:
    #             select()
    #         else:
    #             # 如果不在这个时间段 休眠长一点
    #             time.sleep(20 * 60)
    #     except Exception as e:
    #         logging.error(e)
    #         print(e)
    #
    #     time.sleep(60)



    #测试
    while True:
        post_taobaoke_url(wx_id='wxid_cegmcl4xhn5w22', group_id='wxid_9zoigugzqipj21', md_username='leyang')
        time.sleep(60 * 60 * 9)

