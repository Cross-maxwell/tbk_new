# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import requests
from django.http import HttpResponse
from django.views.generic.base import View

from ipad_weixin.models import Qrcode, WxUser, ChatRoom
from weixin_scripts.post_taobaoke import post_taobaoke_url

import logging
logger = logging.getLogger('django_views')


class PostGoods(View):
    """
    接口： s-prod-04.qunzhu666.com:8080/push_product
    """
    def get(self, request):
        user_list = WxUser.objects.filter(login__gt=0, is_superuser=False).all()
        logger.info([user.username for user in user_list])

        for user in user_list:
            logger.info('Post Taobaoke Handling nickname: {0}, wx_id: {1}'.format(user.nickname, user.username))
            # 发单机器人id
            wx_id = user.username
            # 通过 wx_id = hid 筛选出手机号
            qr_code_db = Qrcode.objects.filter(username=user.username,
                                               md_username__isnull=False).order_by('-id').first()
            md_username = qr_code_db.md_username
            # 10分钟内不可以连续发送同样的请求。
            rsp = requests.get(
                "http://s-prod-07.qunzhu666.com:8000/api/tk/is-push?username={0}&wx_id={1}".format(md_username, wx_id),
                timeout=4)
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
        return HttpResponse(json.dumps({"ret": 1}))


class SendSignNotice(View):
    """
    接口： http://s-prod-04.qunzhu666.com/send_signin_notice
    """
    def get(self, request):
        wxuser_list = WxUser.objects.filter(login__gt=0, is_superuser=False).all()
        for wx_user in wxuser_list:
            chatroom_list = ChatRoom.objects.filter(wx_user__username=wx_user.username,
                                                    nickname__icontains=u"福利社").all()
            for chatroom in chatroom_list:
                import thread
                thread.start_new_thread(self.send_nitice, (wx_user, chatroom))
        return HttpResponse(json.dumps({"ret": 1}))

    def send_nitice(self, wx_user, chatroom):
        text_msg_dict = {
            # 群主 id
            "uin": wx_user.username,
            # 群/联系人 id
            "group_id": chatroom.username,
            "text": "签到开始了，回复 {0} 就可以签到哦～".format("你想要的这里都有"),
            "type": "text",
            "delay_time": 40
        }

        img_msg_dict = {
            "uin": wx_user.username,
            "group_id": chatroom.username,
            "text": "http://ww4.sinaimg.cn/large/0060lm7Tly1fkt5khyyygj30hs0s074z.jpg",
            "type": "img"
        }

        from ipad_weixin.send_msg_type import send_msg_type
        send_msg_type(img_msg_dict, at_user_id='')
        send_msg_type(text_msg_dict, at_user_id='')


