# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import threading
import requests

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from broadcast.models.user_models import TkUser, Adzone
from broadcast.serializers.user_serializers import AdzoneSerializer, TkUserSerializer
from broadcast.utils import generatePoster_ran
from user_auth.models import PushTime
from django.views.generic.base import View

sys.path.append('/home/new_taobaoke/taobaoke/')
from fuli import top_settings


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
    # adzone_id = request.GET.get('adzone_id')
    # if adzone_id is not None:
    #     tk_user = TkUser.objects.get(adzone__pid__contains=adzone_id)
    tk_user = request.user.tkuser
    return Response(TkUserSerializer(tk_user).data)


@api_view(['GET'])
def get_login_qrcode(request):
    from scripts.alimama.sales_data.fetch_cookie import fetch_cookie_from_network
    threading.Thread(target=fetch_cookie_from_network).start()
    return Response(u"Bot is sending qr code snap through Bearychat, you can close this website now")

@csrf_exempt
def poster_url(request):
    if request.method == 'GET':
        url = request.GET['url'] or None
        pic_url = generatePoster_ran(url)
        response_data = {'url': pic_url}
        return JsonResponse(response_data, status=200)

def get_invite_code(request):
    if request.method == 'GET':
        user = request.user
        try:
            invite_code = user.tkuser.invite_code
            data = {'invite_code':invite_code}
            return  HttpResponse(json.dumps({'data': data}),status=200)
        except TkUser.DoesNotExist:
            return  HttpResponse(json.dumps({'error':'TkUser does not exist.'}),status=400)
        except Exception,e:
            return  HttpResponse(json.dumps({'error': e.message}),status=400)

def get_openid(request):
    code = request.GET.get('code', '')
    username = request.GET.get('username', '')
    print 'code:' + code + '-----username:' + username
    try:
        if code and username:
            user_id = User.objects.get(username=username).id
            tkuser= TkUser.objects.filter(user_id=user_id).first()
            OPENID=''
            if tkuser:
                OPENID = tkuser.openid
            if not OPENID:
                url = 'https://api.weixin.qq.com/sns/oauth2/access_token?' \
                      'appid={APPID}&secret={SECRET}&code={CODE}&grant_type=authorization_code' \
                    .format(APPID=top_settings.APPID, SECRET=top_settings.APPSECRET, CODE=code)
                res = requests.get(url)
                json_date = res.json()
                print json_date
                open_id = json_date.get("openid", '')
                print 'open_id:' + open_id
                if open_id:
                    # 存数据库
                    user_id = User.objects.get(username=username).id
                    TkUser.objects.filter(user_id=user_id).update(openid=open_id)
            return HttpResponse('ok')
    except Exception as e:
        print e
    return HttpResponse('bad')

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


class GetPushTIme(View):
    def get(self, request):
        user = request.user
        pushtime = PushTime.objects.get(user=user)
        interval_time = pushtime.interval_time
        begin_time = pushtime.begin_time
        end_time = pushtime.end_time
        return HttpResponse(json.dumps({"interval_time": interval_time,
                                        "begin_time": begin_time, "end_time": end_time}))