# -*- encoding: utf-8 -*-

from django.conf.urls import url
from .views import GetQrcode, HostList, IsLogin, IsUuidLogin, AddSendGroup


urlpatterns = [
    url(r'get_qrcode/',GetQrcode.as_view()),

    #09-21 该接口暂未测试
    url(r'host_list/', HostList.as_view()),
    url(r'is_login/', IsLogin.as_view()),
    url(r'is_uuid_login/', IsUuidLogin.as_view()),

    url(r'send_groups/', AddSendGroup.as_view())
]