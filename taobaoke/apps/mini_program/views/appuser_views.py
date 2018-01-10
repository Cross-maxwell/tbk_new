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
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin


from mini_program.settings import AppID, AppSecret, MCH_ID, IP, notify_url
from mini_program.models.payment_models import Payment, AppUser, UserAddress, AppSession, PaymentOrder
from mini_program.serializer import AppUserAddressSerializer, PaymentOrderSerializer

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
        encryption_session_key = hashlib.sha512(session_key + session_key[:6]).hexdigest()

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

        return HttpResponse(json.dumps({"encryption_session_key": encryption_session_key}), status=200)


class AddOrUpdateUserAddress(View):
    def post(self, request):
        """
        根据encrption_session_key创建一个收货地址
        """
        try:
            req_dict = json.loads(request.body)
            session_key = req_dict.get("encryption_session_key", "")
            phone_num = req_dict.get("phone_num", "")
            name = req_dict.get("name", "")
            address = req_dict.get("address", "")
            address_id = req_dict.get("address_id", "")
            if not phone_num or not name or not address:
                return HttpResponse(json.dumps({"ret": 0, "data": "参数缺失"}), status=400)

            try:
                if session_key:
                    app_user = AppUser.objects.get(appsession__encryption_session_key=session_key)
                else:
                    raise Http404
            except Exception as e:
                logger.error(e)
                return HttpResponse(json.dumps({"ret": 0, "data": "错误的session_key"}))

            if not address_id:
                # 若address_id不存在，则为创建地址
                user_address = UserAddress.objects.create(phone_num=phone_num, name=name,
                                                          address=address, app_user=app_user)
            if address_id:
                # 若address_id存在，则为更新地址
                data = {
                    "phone_num": phone_num,
                    "name": name,
                    "address": address
                }
                try:
                    user_address_id = UserAddress.objects.filter(id=address_id, app_user=app_user).update(**data)
                    user_address = UserAddress.objects.get(id=address_id, app_user=app_user)
                except UserAddress.DoesNotExist:
                    return HttpResponse(json.dumps({"ret": 0, "data": "address不存在"}), status=400)

            serializer = AppUserAddressSerializer(user_address)
            return HttpResponse(json.dumps({"result": serializer.data}))
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({"ret": 0, "data": "未知错误"}), status=500)


class GetUserAddress(View):
    def post(self, request):
        req_dict = json.loads(request.body)
        encryption_session_key = req_dict.get("encryption_session_key", "")
        address_id = req_dict.get("address_id", "")
        if not encryption_session_key:
            return HttpResponse(json.dumps({"ret": 0, "data": "参数缺失"}), status=400)
        try:
            app_user = AppUser.objects.get(appsession__encryption_session_key=encryption_session_key)
        except Exception as e:
            return HttpResponse(json.dumps({"ret": 0, "data": "用户不存在"}), status=400)
        if not address_id:
            # 获取所有地址
            user_address = UserAddress.objects.filter(app_user=app_user)
        if address_id:
            # 获取单个地址
            user_address = UserAddress.objects.filter(app_user=app_user, id=address_id)

        serializer = AppUserAddressSerializer(user_address, many=True)
        return HttpResponse(json.dumps({"result": serializer.data}))


class GetUserPaymentOrder(View):
    """
    获取用户订单
    """
    def post(self, request):
        req_dict = json.loads(request.body)
        encryption_session_key = req_dict.get("encryption_session_key", "")
        if not encryption_session_key:
            return HttpResponse(json.dumps({"ret": 0, "data": "参数缺失"}), status=400)
        try:
            app_user = AppUser.objects.get(appsession__encryption_session_key=encryption_session_key)
        except Exception as e:
            return HttpResponse(json.dumps({"ret": 0, "data": "用户不存在"}), status=400)
        payment_order = PaymentOrder.objects.filter(app_user=app_user)
        serializer = PaymentOrderSerializer(payment_order, many=True)
        return HttpResponse(json.dumps({"result": serializer.data}))

