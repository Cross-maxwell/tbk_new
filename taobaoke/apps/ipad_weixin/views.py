# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from broadcast.models.user_models import TkUser
from django.http import HttpResponse
from django.views.generic.base import View

from ipad_weixin.weixin_bot import WXBot
from models import Qrcode, WxUser, ChatRoom, SignInRule
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from weixin_scripts.post_taobaoke import post_taobaoke_url
import requests
import time
import datetime
from django.utils import timezone
from ipad_weixin.heartbeat_manager import HeartBeatManager

import logging
logger = logging.getLogger('django_views')


class GetQrcode(View):
    def get(self, request):
        md_username = request.GET.get('username', '')

        wx_bot = WXBot()
        (oss_path, qrcode_rsp, deviceId) = wx_bot.get_qrcode(md_username)

        import thread
        thread.start_new_thread(wx_bot.check_and_confirm_and_load, (qrcode_rsp, deviceId, md_username))

        response_data = {"qrcode_url": oss_path}
        return HttpResponse(json.dumps(response_data), content_type="application/json")

"""
新版本， 待前端完成后推送
"""
# class HostList(View):
#     # username是手机号
#     def get(self, request):
#         username = request.GET.get('username', '')
#         data = []
#         try:
#             # 第一步 筛选出这个人登录了多少个机器人 并且取出它的wx_id
#             wxusers = WxUser.objects.filter(user__username=username).all()
#             for wxuser in wxusers:
#                 robot_chatroom_list = []
#                 ret = wxuser.login
#                 name = wxuser.nickname
#                 chatroom_list = ChatRoom.objects.filter(wx_user__username=wxuser.username, nickname__contains=u"福利社")
#                 for chatroom in chatroom_list:
#                     robot_chatroom_list.append(chatroom.nickname)
#                 data.append({"ret": ret, "name": name, "group": robot_chatroom_list})
#         except Exception as e:
#             logger.error(e)
#             print(e)
#         response_data = {"data": data}
#         return HttpResponse(json.dumps(response_data))


class HostList(View):
    def get(self, request):
        username = request.GET.get('username', '')
        ret = 0
        data = []
        try:
            # 第一步 筛选出这个人登录了多少个机器人 并且取出它的wx_id
            wxusers = WxUser.objects.filter(user__username=username).all()
            for wxuser in wxusers:
                ret = wxuser.login
                name = wxuser.nickname
                chatroom_list = ChatRoom.objects.filter(wx_user__username=wxuser.username, nickname__contains=u"福利社")
                for chatroom in chatroom_list:
                    data.append({"ret": ret, "name": name, "group": chatroom.nickname})
        except Exception as e:
            logger.error(e)
            print(e)

        response_data = {"ret": str(ret), "data": data}

        return HttpResponse(json.dumps(response_data))


class IsLogin(View):
    """
    http://localhost:5000/is_login?username=15900000010
    """
    def get(self, request):
        username = request.GET.get('username', '')
        if 'username' == '':
            response_data = {"ret": str(0), "name": "未登录"}
            return HttpResponse(json.dumps(response_data))
        ret = 0
        name = ''
        try:
            # username是手机号
            qr_code_db = Qrcode.objects.filter(md_username=username, username__isnull=False).order_by('-id').first()
            wx_username = qr_code_db.username
            print(wx_username)

            # 筛选出wx用户昵称
            wxuser = WxUser.objects.filter(username=wx_username).order_by('-id').first()
            ret = wxuser.login
            name = wxuser.nickname

            print(name.encode('utf8'))
        except Exception as e:
            logger.error(e)
            print(e)

        response_data = {"ret": str(ret), "name": name}
        return HttpResponse(json.dumps(response_data))


class IsUuidLogin(View):
    """
    检测该UUID是否被扫描登陆
    # http://localhost:5000/is-uuid-login?qr-uuid=gZF8miqrkksZ9mrRk7mc
    :return:返回登陆的微信 nickname 和 login 状态
    """
    def get(self, request):
        qr_uuid = request.GET.get('qr-uuid', '')
        if qr_uuid == '':
            response_data = {"ret": str(0), "name": "qr-uuid 为空"}
            return HttpResponse(json.dumps(response_data))
        ret = 0
        name = ''
        try:
            # username是手机号
            qr_code_db = Qrcode.objects.filter(uuid=qr_uuid).first()
            if qr_code_db is not None and qr_code_db.username != '':
                wx_username = qr_code_db.username
                # 筛选出wx_username
                print wx_username

                # 筛选出wx用户昵称
                user_db = WxUser.objects.filter(username=wx_username).first()
                ret = user_db.login
                name = user_db.nickname
        except Exception as e:
            logger.error(e)
            print(e)
        # name <type 'unicode'>
        response_data = {"ret": str(ret), "name": name}
        return HttpResponse(json.dumps(response_data))


class PostGoods(View):
    """
    接口： s-prod-04.qunzhu666.com/push_product
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



class DefineSignRule(View):
    """
    接口： http://s-prod-04.qunzhu666.com/define_sign_rule
    """
    @csrf_exempt
    def post(self, request):
        req_dict = json.loads(request.body)
        keyword = req_dict['keyword']
        md_username = req_dict['md_username']
        # 目前web接口只提供 “福利社” 的红包id
        red_packet_id = 'oGO5ABhwpqFyNBhmuUHR'
        wx_user = WxUser.objects.filter(user__username=md_username).first()
        chatroom_list = ChatRoom.objects.filter(wx_user__username=wx_user.username, username__icontains=u"福利社")
        if not chatroom_list:
            return HttpResponse(json.dumps({"ret": 0, "reason": "发单群为空"}))
        sign_rule = SignInRule()
        sign_rule.keyword = keyword
        sign_rule.red_packet_id = red_packet_id
        sign_rule.save()

        for chatroom in chatroom_list:
            sign_rule.chatroom.add(chatroom.id)
            sign_rule.save()

        return HttpResponse(json.dumps({"ret": 1, "reason": "添加红包口令成功"}))


class ResetHeartBeat(View):
    """
    此方法只能在重启supervisor服务时使用，系统运行时严禁使用该接口
    """
    def get(self, request):
        auth_users = WxUser.objects.filter(last_heart_beat__gt=timezone.now() - datetime.timedelta(minutes=300))
        if not auth_users:
            logger.info("重启心跳用户数为0")
        for auth_user in auth_users:
            logger.info("%s command 开启心跳" % auth_user.nickname)
            # 清空心跳列表
            if auth_user.username in HeartBeatManager.heartbeat_thread_dict:
                del HeartBeatManager.heartbeat_thread_dict[auth_user.username]
            HeartBeatManager.begin_heartbeat(auth_user.username)
        return HttpResponse(json.dumps({"ret": 1}))


class ResetSingleHeartBeat(View):
    """
    开启单个用户心跳
    接口： http://s-prod-04.qunzhu666.com/reset_single?username=wx_id
    """
    def get(self, request):
        username = request.GET.get('username')
        if username in HeartBeatManager.heartbeat_thread_dict:
            del HeartBeatManager.heartbeat_thread_dict[username]
        HeartBeatManager.begin_heartbeat(username)
        return HttpResponse(json.dumps({"ret": 1}))


class AddSuperUser(View):
    """
    接口: http://s-prod-04.qunzhu666.com/add_super_user?username=wx_id
    """
    def get(self, request):
        username = request.GET.get('username')
        wx_user = WxUser.objects.get(username=username)
        if wx_user:
            wx_user.is_superuser = True
            wx_user.save()
            return HttpResponse(json.dumps({"ret": u"add superuser successfully"}))
        else:
            return HttpResponse(json.dumps({"ret": u"add superuser failed"}))


class SendSignNotice(View):
    def get(self, request):
        wxuser_list = WxUser.objects.filter(login__gt=0, is_superuser=False).all()
        for wx_user in wxuser_list:
            chatroom_list = ChatRoom.objects.filter(wx_user__username=wx_user.username,
                                                    nickname__icontains=u"测试福利社").all()
            for chatroom in chatroom_list:
                text_msg_dict = {
                    # 群主 id
                    "uin": wx_user.username,
                    # 群/联系人 id
                    "group_id": chatroom.username,
                    "text": "签到开始了，回复 {0} 就可以签到哦～".format("正在测试"),
                    "type": "text",
                    "delay_time": 40
                }

                img_msg_dict = {
                    "uin": wx_user.username,
                    "group_id": chatroom.username,
                    "text": "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1508657613624&di=407a48fabc04e6e445cb26f751f8737b&imgtype=0&src=http%3A%2F%2Fimg4.duitang.com%2Fuploads%2Fitem%2F201507%2F25%2F20150725014419_as3cW.jpeg",
                    "type": "img"
                }
                from ipad_weixin.send_msg_type import send_msg_type
                send_msg_type(img_msg_dict, at_user_id='')

                send_msg_type(text_msg_dict, at_user_id='')
        return HttpResponse(json.dumps({"ret": 1}))












