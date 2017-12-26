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
from django.core import serializers

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin


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


# class AddUserAddress(View):
#     def post(self, request):
#         req_dict = json.loads(request.body)
#         openid = req_dict.get("openid", "")
#         phone_num = req_dict.get("phone_num", "")
#         name = req_dict.get("name", "")
#         address = req_dict.get("address", "")
#         if not (openid or phone_num or name or address):
#             return HttpResponse(json.dumps({"ret": 0, "data": "参数缺失"}), status=400)
#         try:
#             app_user = AppUser.objects.get(openid=openid)
#         except Exception as e:
#             return HttpResponse(json.dumps({"ret": 0, "data": "用户不存在"}), status=400)
#         data_list = []
#         user_address = UserAddress.objects.create(phone_num=phone_num, name=name,
#                                                   address=address, app_user=app_user)
#         data_list.append(user_address)
#         # 这里只能序列化List
#         json_data = serializers.serialize("json", user_address)
#         return HttpResponse(json_data, content_type="application/json")


from mini_program.serializer import AppUserAddressSerializer
from rest_framework.response import Response


class AddUserAddress(APIView):
    def get(self, request):
        openid = request.GET.get("openid")
        address_db = UserAddress.objects.filter(openid=openid)
        products_serializer = AppUserAddressSerializer(address_db, many=True)
        return Response(products_serializer.data)
    def post(self, request):
        pass
    def put(self, request):
        pass


