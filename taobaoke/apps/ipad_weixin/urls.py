# -*- encoding: utf-8 -*-

from django.conf.urls import url
from .views import GetQrcode, HostList, IsLogin, IsUuidLogin, PostGoods



urlpatterns = [
    url(r'getqrcode/',GetQrcode.as_view()),
    url(r'host_list/', HostList.as_view()),
    url(r'is_login/', IsLogin.as_view()),
    url(r'is-uuid-login/', IsUuidLogin.as_view()),
    url(r'push_product', PostGoods.as_view())
]



