# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import requests
import datetime
import random
from django.http import HttpResponse
from django.views.generic.base import View
from django.core.cache import cache
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from broadcast.models.user_models import TkUser
from broadcast.models.entry_models import Product
from django.db.models import Q
from user_auth.models import PushTime
import urllib
from broadcast.models.user_models import Adzone
from django.utils.encoding import iri_to_uri
from fuli.oss_utils import beary_chat
import random
from broadcast.models.entry_models import PushRecord

import logging
logger = logging.getLogger('django_views')


class PushProduct(View):
    def get(self, request):
        # 随机筛选商品
        # TODO: 为了解决推送记录的记录，则先筛选user，而非先筛选商品
        platform_id = 'make_money_together'

        # 本地测试
        # 获取登录了一起赚平台的所有user列表
        # url = "http://localhost:10024/robot/platform_user_list?platform_id={}".format(platform_id)
        # send_msg_url = 'http://localhost:10024/robot/send_msg/'

        url = "http://s-prod-04.qunzhu666.com:10024/robot/platform_user_list?platform_id={}".format(platform_id)

        send_msg_url = 'http://s-prod-04.qunzhu666.com:10024/robot/send_msg/'
        # url = "http://s-prod-04.qunzhu666.com:8080/robot/xxxx?platform_key={}".format(platform_id)

        response = requests.get(url)
        response_dict = json.loads(response.content)
        if response_dict["ret"] != 1:
            logger.error("筛选{}平台User为空".format(platform_id))
        login_user_list = response_dict["login_user_list"]

        """
        {
            "login_user_list":[
                    {"user": "smart", "wxuser_list": ["樂阳", "渺渺的"]}，
                    {"user": "keyerror", ......}
            ]
        }
        """
        for user_object in login_user_list:
            user = user_object["user"]

            # 找到该user所对应的pid
            try:
                tk_user = TkUser.get_user(user)
            except Exception as e:
                logger.error(e)
            try:
                pid = tk_user.adzone.pid
            except Exception as e:
                logger.error('{0} 获取Adzone.pid失败, reason: {1}'.format(user, e))

            wxuser_list = user_object["wxuser_list"]

            # 根据phone_num判定是否到达发单时间
            ret = is_push(user, platform_id)
            if ret == 0:
                logger.info("%s 未到发单时间" % wxuser_list)
            if ret == 1:
                qs = Product.objects.filter(
                    ~Q(pushrecord__user_key__icontains=user,
                       pushrecord__create_time__gt=timezone.now() - datetime.timedelta(days=3)),
                    available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
                )

                # 用发送过的随机商品替代
                if qs.count() == 0:
                    qs = Product.objects.filter(
                        available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
                    )
                    beary_chat('点金推送商品失败：%s:%s 无可用商品' % (user, user_object["wxuser_list"]))

                for _ in range(50):
                    try:
                        r = random.randint(0, qs.count() - 1)
                        p = qs.all()[r]
                        break
                    except Exception as exc:
                        print "Get entry exception. Count=%d." % qs.count()
                        logger.error(exc)

                text = p.get_text_msg(pid=pid)
                img_url = p.get_img_msg()
                data = [img_url, text]

                request_data = {
                    "md_username": user,
                    "data": data
                }
                PushRecord.objects.create(entry=p, user_key=user)
                send_msg_response = requests.post(send_msg_url, data=json.dumps(request_data))

        return HttpResponse(json.dumps({"ret": 1}))


class AcceptSearchView(View):
    @csrf_exempt
    def post(self, request):
        req_dict = json.loads(request.body)
        username = req_dict["md_username"]
        at_user_nickname = req_dict["at_user_nickname"]
        keyword = req_dict["keyword"]

        adzone_db = Adzone.objects.filter(tkuser__user__username=username).first()
        pid = adzone_db.pid

        template_url = 'http://dianjin.dg15.cn/saber/index/search?pid={0}&search={1}'.format(pid, keyword)
        judge_url = 'http://dianjin.dg15.cn/a_api/index/search?wp=&sort=3&pid={0}&search={1}&_path=9001.SE.0'.format(
            pid, keyword)
        judge_response = requests.get(judge_url)
        judge_dict = json.loads(judge_response.content)

        if not judge_dict['result']['items']:
            text = u"{0}，很抱歉，您需要的{1}没有找到，您可以搜索一下其他商品哦～[太阳][太阳]".format(at_user_nickname, keyword)
            data = [text]
        else:
            # 重载template_url, 用于从微博api获取短链
            template_url = urllib.quote(iri_to_uri(template_url))
            short_url_respose = requests.get(
                'http://api.weibo.com/2/short_url/shorten.json?source=2849184197&url_long=' + template_url)
            short_url = short_url_respose.json()['urls'][0]['url_short']

            random_seed = random.randint(1000, 2000)
            text = "{0}，搜索  {1}  成功！此次共搜索到相关产品{2}件，点击链接查看为您找到的天猫高额优惠券。\n" \
                   "{3}\n" \
                   "「点击上面链接查看宝贝」\n" \
                   "================\n" \
                   "图片仅供参考，详细信息请点击链接～".format(at_user_nickname, keyword, random_seed, short_url)

            img_url = judge_dict['result']['items'][0]['coverImage']
            data = [img_url, text]

        return HttpResponse(json.dumps({"data": data}))


def is_push(md_username, wx_id):
    """
    md_username
    wx_id
    """
    try:
        pushtime = PushTime()
        user_pt = pushtime.get_pushtime(md_username)
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


class AppProductJsonView(View):
    def get(self, request):
        # 返回商品的类别，
        pass


# class SendSignNotice(View):
#     """
#     接口： http://s-prod-04.qunzhu666.com/tk/send_signin_notice
#     """
#     def get(self, request):
#         wxuser_list = WxUser.objects.filter(login__gt=0, is_customer_server=False).all()
#         for wx_user in wxuser_list:
#             chatroom_list = ChatRoom.objects.filter(wx_user__username=wx_user.username,
#                                                     nickname__icontains=u"福利社").all()
#             for chatroom in chatroom_list:
#                 import thread
#                 thread.start_new_thread(self.send_nitice, (wx_user, chatroom))
#         return HttpResponse(json.dumps({"ret": 1}))
#
#     def send_nitice(self, wx_user, chatroom):
#         text_msg_dict = {
#             # 群主 id
#             "uin": wx_user.username,
#             # 群/联系人 id
#             "group_id": chatroom.username,
#             "text": "签到开始了，回复 {0} 就可以签到哦～".format("你想要的这里都有"),
#             "type": "text",
#             "delay_time": 40
#         }
#
#         img_msg_dict = {
#             "uin": wx_user.username,
#             "group_id": chatroom.username,
#             "text": "http://ww4.sinaimg.cn/large/0060lm7Tly1fkt5khyyygj30hs0s074z.jpg",
#             "type": "img"
#         }
#
#         from ipad_weixin.send_msg_type import send_msg_type
#         send_msg_type(img_msg_dict, at_user_id='')
#         send_msg_type(text_msg_dict, at_user_id='')


