# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import random
import re
import threading
import time
import datetime
import requests
from django.utils import timezone

import scrapy
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.encoding import iri_to_uri
from django.views.decorators.csrf import csrf_exempt
from scrapy.crawler import CrawlerProcess
from django.db.models import Q

from broadcast.models.entry_models import Product, PushRecord
from broadcast.models.user_models import TkUser, Adzone
from broadcast.management.commands.push import push_product
from broadcast.serializers.user_serializers import AdzoneSerializer, TkUserSerializer


"""
由脚本发起的post请求
scripts/fetch_pid
"""

@csrf_exempt
def update_adzone(request):
    req_dict = json.loads(request.body)
    pid, created = Adzone.objects.get_or_create(pid=req_dict['adzonePid'])
    pid.adzone_name = req_dict['name']
    pid.click_30d = req_dict['mixClick30day']
    pid.alipay_num_30d = req_dict['mixAlipayNum30day']
    pid.rec_30d = req_dict['rec30day']
    pid.alipay_rec_30d = req_dict['mixAlipayRec30day']
    pid.save()

    if created:
        return HttpResponse('Created adzone', status=201)
    else:
        return HttpResponse('Updated adzone', status=200)


@api_view(['GET'])
def get_adzone_info(request):
    username = request.GET.get('username', None)
    adzone_id = request.GET.get('adzone_id', None)
    if username is not None:
        adzone = Adzone.objects.get(tkuser__user__username=username)
    elif adzone_id is not None:
        adzone = Adzone.objects.get(pid__contains=adzone_id)
    return Response(AdzoneSerializer(adzone).data)


@api_view(['GET'])
def get_tkuser_info(request):
    adzone_id = request.GET.get('adzone_id')
    if adzone_id is not None:
        tk_user = TkUser.objects.get(adzone__pid__contains=adzone_id)
    return Response(TkUserSerializer(tk_user).data)


@api_view(['GET'])
def get_login_qrcode(request):
    from scripts.alimama.sales_data.fetch_cookie import fetch_cookie_from_network
    threading.Thread(target=fetch_cookie_from_network).start()
    return Response(u"Bot is sending qr code snap through Bearychat, you can close this website now")
