# -*- coding: utf-8 -*-
import re
import random
import json
import requests
import hashlib
import datetime
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt


from mini_program.settings import AppID, AppSecret, MCH_ID, IP, notify_url
from mini_program.models.payment_models import Payment, AppUser, UserAddress, AppSession

import logging
logger = logging.getLogger("django_views")


class GetSessionKey(View):
    @csrf_exempt
    def post(self, request):
        req_dict = json.loads(request.body)
        js_code = req_dict.get("code", "")

        # 获取微信用户信息
        req_dict = json.loads(request.body)
        user_dict = req_dict.get("userName", "")
        nickname = user_dict.get("nickName", "")
        avatar_url = user_dict.get("avatarUrl", "")
        city = user_dict.get("city", "")
        country = user_dict.get("country", "")
        province = user_dict.get("province", "")

        if not js_code:
            return HttpResponse(json.dumps({"ret": 0, "data": "js_code为空"}), status=400)
        api = "https://api.weixin.qq.com/sns/jscode2session?appid={AppID}&secret={AppSecret}&js_code={js_code}&grant_t" \
              "ype=authorization_code".format(AppID=AppID, AppSecret=AppSecret, js_code=js_code)
        resp_dict = json.loads(requests.get(api).content)
        # 获取用户唯一标识
        try:
            session_key = resp_dict["session_key"]
            openid = resp_dict["openid"]
        except KeyError:
            logger.error("GetSessionKey异常")
            return HttpResponse(json.dumps({"ret": 0, "data": "Error"}), status=500)
        encryption_session_key = hashlib.sha512(session_key).hexdigest()

        app_user_dict = {
            "nickname": nickname,
            "avatar_url": avatar_url,
            "city": city,
            "country": country,
            "province": province,
            "openid": openid
        }

        app_user, created = AppUser.objects.update_or_create(openid=openid, defaults=app_user_dict)

        session_dict = {
            "session_key": session_key,
            "encryption_session_key": encryption_session_key,
            "expire_day": datetime.datetime.now() + datetime.timedelta(days=30),
        }
        app_session, created = AppSession.objects.update_or_create(app_user=app_user, defaults=session_dict)

        return HttpResponse(json.dumps({"openid": openid, "encryption_session_key": encryption_session_key}), status=200)