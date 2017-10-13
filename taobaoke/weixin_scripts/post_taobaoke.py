# -*- coding: utf-8 -*-
"""
淘宝客推送脚本, 向已经激活的、带有“福利社”的群组推送从lanlanlife取得的商品。post_taobaoke_url测试正常
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

BASE_DIRS = '/home/smartkeyerror/PycharmProjects/taobaoke/taobaoke/'
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
    send_msg_type(img_msg_dict)
    logger.info("%s 向 %s 推送图片 ." % (img_msg_dict['text'], img_msg_dict['group_id']))

    send_msg_type(text_msg_dict)
    logger.info("%s 向 %s 推送文字 ." % (img_msg_dict['text'], img_msg_dict['group_id']))



def select():
    # 筛选出已经登录的User
    user_list = WxUser.objects.filter(login__gt = 0).all()
    logger.info([user.username for user in user_list])

    for user in user_list:
        logger.info('Handling nickname: {0}, wx_id: {1}'.format(user.nickname, user.username))
        # 发单机器人id
        wx_id = user.username
        # 通过 wx_id = hid 筛选出手机号
        qr_code_db = Qrcode.objects.filter(username=user.username, md_username__isnull=False).order_by('-id').first()
        md_username = qr_code_db.md_username
        # 10分钟内不可以连续发送同样的请求。
        rsp = requests.get("http://s-prod-07.qunzhu666.com:8000/api/tk/is-push?username={0}&wx_id={1}".format(md_username, wx_id), timeout=4)
        ret = json.loads(rsp.text)['ret']
        if ret == 0:
            logger.info("%s 请求s-prod-07返回结果为0" % user.nickname)

        if ret == 1:
            # 筛选出激活群
            wxuser = WxUser.objects.filter(username=user.username).order_by('-id').first()
            chatroom_list = ChatRoom.objects.filter(wx_user=wxuser.id, nickname__contains=u"福利社").all()
            if not chatroom_list:
                logger.info('%s 发单群为空' % wxuser.nickname)

            for chatroom in chatroom_list:
                # 发单人的wx_id, 群的id, 手机号
                try:
                    group_id = chatroom.username
                    logger.info(u'%s 向 %s 推送商品' % (wxuser.nickname, chatroom.nickname))

                    import thread
                    thread.start_new_thread(post_taobaoke_url, (wx_id, group_id, md_username))
                except Exception as e:
                    logging.error(e)
                    print(e)

if __name__ == "__main__":
    while True:
        try:
            now_hour = int(time.strftime('%H', time.localtime(time.time())))
            if 7 <= now_hour <= 22:
                select()
            else:
                # 如果不在这个时间段 休眠长一点
                time.sleep(20 * 60)
        except Exception as e:
            logging.error(e)
            print(e)

        time.sleep(60)



    #测试
    # while True:
    #     wxuser = WxUser.objects.filter(username='wxid_cegmcl4xhn5w22').order_by('-id').first()
    #     chatroom_list = ChatRoom.objects.filter(wx_user=wxuser.id, nickname__contains=u"测试福利社").all()
    #     wx_id = 'wxid_cegmcl4xhn5w22'
    #     md_username = '13632909405_l'
    #
    #     for chatroom in chatroom_list:
    #         # 发单人的wx_id, 群的id, 手机号
    #         try:
    #             group_id = chatroom.username
    #             logger.info(u'向 %s 推送商品' % chatroom.nickname)
    #
    #             # import thread
    #             #
    #             # thread.start_new_thread(post_taobaoke_url, (wx_id, group_id, md_username))
    #             # time.sleep(60 * 5)
    #             post_taobaoke_url(wx_id, group_id, md_username)
    #             time.sleep(60 * 5)
    #         except Exception as e:
    #             logging.error(e)
    #             print(e)


