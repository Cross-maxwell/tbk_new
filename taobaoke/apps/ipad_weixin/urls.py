# -*- encoding: utf-8 -*-

from django.conf.urls import url
from .views import GetQrcode, HostList, IsLogin, IsUuidLogin
from django.utils import timezone
import datetime


urlpatterns = [
    url(r'getqrcode/',GetQrcode.as_view()),
    url(r'host_list/', HostList.as_view()),
    url(r'is_login/', IsLogin.as_view()),
    url(r'is-uuid-login/', IsUuidLogin.as_view()),
]

from ipad_weixin.models import WxUser
from ipad_weixin.heartbeat_manager import HeartBeatManager

auth_users = WxUser.objects.filter(last_heart_beat__gt=timezone.now() - datetime.timedelta(minutes=60))
for auth_user in auth_users:
    HeartBeatManager.begin_heartbeat(auth_user.username)

