# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from broadcast.models.user_models import TkUser
from django.http import HttpResponse
from django.views.generic.base import View

from ipad_weixin.weixin_bot import WXBot
from models import Qrcode, WxUser, ChatRoom
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

import logging
logger = logging.getLogger('django_views')


class GetQrcode(View):
    def get(self, request):
        md_username = request.GET.get('username', '')

        wx_bot = WXBot()
        (oss_path, qrcode_rsp, deviceId) = wx_bot.get_qrcode(md_username)

        try:
            buffers = qrcode_rsp.baseMsg.payloads
            qr_code = json.loads(buffers)
            uuid = qr_code['Uuid']
            qr_code_db = Qrcode.objects.filter(uuid=uuid).order_by('-id').first()
            qr_code_db.md_username = md_username
            qr_code_db.save()
        except Exception as e:
            logger.error(e)
            print(e)


        import thread
        thread.start_new_thread(wx_bot.check_and_confirm_and_load, (qrcode_rsp, deviceId))

        response_data = {"qrcode_url": oss_path}
        return HttpResponse(json.dumps(response_data), content_type="application/json")



class HostList(View):
    """
    登陆接口 返回 昵称 群名
    :return:
    """
    # username是手机号
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

            # qr_code_db = Qrcode.objects.filter(md_username=username).order_by('-id').all()
            # wx_id_set = set([qr_code.username for qr_code in qr_code_db if qr_code.username != ''])
            #
            # for wx_id in wx_id_set:
            #
            #     # 筛选出wx用户昵称
            #     user_db = WxUser.objects.filter(username=wx_id).first()
            #     ret = user_db.login
            #     name = user_db.nickname
            #
            #
            #     # 筛选出这个wx_id激活的群id
            #     message_list = Message.objects.filter(content__contains="激活",
            #                                           from_username=wx_id).all()
            #     group_set = set([message.to_username for message in message_list])
            #     for group in group_set:
            #         # 发单人的wx_id, 群名, 是否登陆了
            #         try:
            #             contact_db = Contact.objects.filter(nickname__contains="福利社", username=group).first()
            #             data.append({"ret": ret, "name": name, "group": contact_db.nickname})
            #         except Exception as e:
            #             print(e)
        except Exception as e:
            logger.error(e)
            print(e)

        response_data = {"ret": str(ret), "data": data}
        return HttpResponse(json.dumps(response_data))


class IsLogin(View):
    """
    登陆接口 返回 昵称 群名
    # http://localhost:5000/is_login?username=15900000010
    :return:
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
            qr_code_db = Qrcode.objects.filter(md_username=username).order_by('-id').all()
            for qr_code in qr_code_db:
                if qr_code.username != '':
                    wx_username = qr_code.username
            # 筛选出wx_username
            print(wx_username)


            # 筛选出wx用户昵称
            wxuser = WxUser.objects.filter(username=wx_username).first()
            ret = wxuser.login
            name = wxuser.nickname

            tk_user = TkUser.get_user(username)
            wxuser.user.add(tk_user.user)
            wxuser.save()

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


















