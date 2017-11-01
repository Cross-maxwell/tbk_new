# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import requests
import datetime
from django.http import HttpResponse
from django.views.generic.base import View
from django.core.cache import cache
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from ipad_weixin.models import Qrcode, WxUser, ChatRoom
from weixin_scripts.post_taobaoke import post_taobaoke_url
from broadcast.models.user_models import PushTime


import logging
logger = logging.getLogger('django_views')

#795318
class PostGoods(View):
    """
    接口： s-prod-04.qunzhu666.com:8080/tk/push_product
    """
    def get(self, request):
        user_list = WxUser.objects.filter(login__gt=0, is_customer_server=False).all()
        logger.info([user.username for user in user_list])

        for user in user_list:
            logger.info('Post Taobaoke Handling nickname: {0}, wx_id: {1}'.format(user.nickname, user.username))
            # 发单机器人id
            wx_id = user.username
            # 通过 wx_id = hid 筛选出手机号
            qr_code_db = Qrcode.objects.filter(username=user.username,
                                               md_username__isnull=False).order_by('-id').first()
            md_username = qr_code_db.md_username

            ret = is_push(md_username, wx_id)
            if ret == 0:
                logger.info("%s 还没有到发单时间" % user.nickname)

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
    接口： http://s-prod-04.qunzhu666.com/tk/send_signin_notice
    """
    def get(self, request):
        wxuser_list = WxUser.objects.filter(login__gt=0, is_customer_server=False).all()
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


class SetPushTime(View):
    @csrf_exempt
    def post(self, request):
        req_data = json.loads(request.body)
        interval_time = int(req_data.get('interval_time', 5))
        begin_time = req_data.get('begin_time')
        end_time = req_data.get('end_time')
        try:
            pushtime = PushTime.objects.get(user=request.user)
            pushtime.interval_time = interval_time
            pushtime.begin_time = begin_time
            pushtime.end_time = end_time
            pushtime.save()
        except PushTime.DoesNotExist:
            pushtime = PushTime.objects.create(user=request.user,
                                               interval_time=interval_time, begin_time=begin_time, end_time=end_time)
        data = {
            "interval_time": interval_time,
            "begin_time": begin_time,
            "end_time": end_time,
            "is_valid": True,
        }

        return HttpResponse(json.dumps({'retCode': 200, 'data': data}))

"""
{
    "data":{
        "id":"59ed9ed7b851f603b7e8187e",
        "md_user_id":"1695",
        "interval_time":50,
        "begin_time":"07:30",
        "end_time":"23:45",
        "is_valid":true,
        "update_time":"2017-10-24T16:40:18.023824"
    },
    "retCode":200
}

"""
def is_push(md_username, wx_id):
    """
    md_username
    wx_id
    """
    try:
        user_pt, created = PushTime.objects.get_or_create(user__username=md_username)
        push_interval = user_pt.interval_time

        cache_key = md_username + '_' + wx_id + '_last_push'
        cache_time_format = "%Y-%m-%d %H:%M:%S"

        cur_time = datetime.datetime.now()
        # 上一次推送的时间
        last_push_time = cache.get(cache_key)
        if last_push_time is None:
            is_within_interval = True
        else:
            dt_last_push_time = datetime.datetime.strptime(last_push_time, cache_time_format)
            is_within_interval = dt_last_push_time + datetime.timedelta(minutes=int(push_interval)) <= cur_time

        dt_begin_pt = datetime.datetime.strptime(user_pt.begin_time.replace('24:00', '23:59'), '%H:%M')
        dt_end_pt = datetime.datetime.strptime(user_pt.end_time.replace('24:00', '23:59'), '%H:%M')

        if dt_begin_pt.time() < cur_time.time() < dt_end_pt.time() and is_within_interval:
            ret_code = 1
            cache.set(cache_key, datetime.datetime.strftime(cur_time, cache_time_format), 3600 * 10)
        else:
            ret_code = 0

        return ret_code
    except Exception as e:
        logger.error(e)


