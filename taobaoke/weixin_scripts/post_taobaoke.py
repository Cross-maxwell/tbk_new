# -*- coding: utf-8 -*-
"""
部署在s-proc-04 supervisor上，可直接访问 s-prod-04.qunzhu666.com:9001 (admin/123456)
"""
import sys
# 脚本加入搜索路径 现在是hard code状态 看看有没有办法改
sys.path.append('/home/new_taobaoke/taobaoke')
# sys.path.append('/home/smartkeyerror/PycharmProjects/new_taobaoke/taobaoke')

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

from ipad_weixin.models import Qrcode, Message, WxUser, Contact, ChatRoom
from ipad_weixin.send_msg_type import send_msg_type
from broadcast.models.user_models import TkUser
from broadcast.models.entry_models import Product, PushRecord
from ipad_weixin.utils.oss_utils import beary_chat



import logging
logger = logging.getLogger('post_taobaoke')


def post_taobaoke_url(wx_id, group_id, md_username):
    # 发单人的wx_id, 群的id, 手机号
    try:
        tk_user = TkUser.get_user(md_username)
    except Exception as e:
        logger.error(e)
    try:
        pid = tk_user.adzone.pid
    except Exception as e:
        logger.error('{0} 获取Adzone.pid失败, reason: {1}'.format(wx_id, e))

    qs = Product.objects.filter(
        ~Q(pushrecord__group__contains=group_id,
           pushrecord__create_time__gt=timezone.now() - datetime.timedelta(days=3)),
        available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
    )

    # 用发送过的随机商品替代
    if qs.count() == 0:
        qs = Product.objects.filter(
            available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
        )
        beary_chat('点金推送商品失败：无可用商品')

    for _ in range(50):
        try:
            r = random.randint(0, qs.count() - 1)
            p = qs.all()[r]
            break
        except Exception as exc:
            print "Get entry exception. Count=%d." % qs.count()
            logger.error(exc)

    # img or text
    text_msg_dict = {
        # 群主 id
        "uin": wx_id,
        # 群/联系人 id
        "group_id": group_id,
        "text": p.get_text_msg(pid=pid),
        "type": "text",
        "delay_time": 40
    }


    img_msg_dict = {
        "uin": wx_id,
        "group_id": group_id,
        "text": p.get_img_msg(),
        "type": "img"
    }

    PushRecord.objects.create(entry=p, group=group_id)
    send_msg_type(img_msg_dict, at_user_id='')
    logger.info("向 %s 推送图片 \n %s." % (img_msg_dict['group_id'], img_msg_dict['text']))

    send_msg_type(text_msg_dict, at_user_id='')
    logger.info("向 %s 推送文字 \n %s." % (text_msg_dict['group_id'], text_msg_dict['text']))










