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
from weixin_scripts.post_taobaoke import post_taobaoke_url
import requests
import time

import logging
logger = logging.getLogger('django_views')


class GetQrcode(View):
    def get(self, request):
        md_username = request.GET.get('username', '')

        wx_bot = WXBot()
        (oss_path, qrcode_rsp, deviceId) = wx_bot.get_qrcode(md_username)

        # try:
        #     buffers = qrcode_rsp.baseMsg.payloads
        #     qr_code = json.loads(buffers)
        #     uuid = qr_code['Uuid']
        #     qr_code_db = Qrcode.objects.filter(uuid=uuid).order_by('-id').first()
        #     qr_code_db.md_username = md_username
        #     qr_code_db.save()
        # except Exception as e:
        #     logger.error(e)
        #     print(e)

        import thread
        thread.start_new_thread(wx_bot.check_and_confirm_and_load, (qrcode_rsp, deviceId, md_username))

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
            qr_code_db = Qrcode.objects.filter(md_username=username, username__isnull=False).order_by('-id').first()
            wx_username = qr_code_db.username
            print(wx_username)

            """
            这个地方的逻辑较为重要，如果写这里，那么必须要发送一个is_login的请求才行。
            现移植到了new_init中
            """
            # 筛选出wx用户昵称
            wxuser = WxUser.objects.filter(username=wx_username).order_by('-id').first()
            ret = wxuser.login
            name = wxuser.nickname

            # 测试
            # tk_user = TkUser.get_user(username)
            # wxuser.user.add(tk_user.user)
            # wxuser.save()

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
        user_list = WxUser.objects.filter(login__gt=0).all()
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
                # return HttpResponse(json.dumps({"ret":0}))

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
        return HttpResponse(json.dumps({"ret":1}))


class DefineSignRule(View):
    def post(self, request):
        req_dict = json.loads(request.body)
        keyword = req_dict['keyword']


















