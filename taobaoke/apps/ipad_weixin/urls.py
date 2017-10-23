# -*- encoding: utf-8 -*-

from django.conf.urls import url
from .views import GetQrcode, HostList, IsLogin, IsUuidLogin, PostGoods, \
    ResetHeartBeat, ResetSingleHeartBeat, DefineSignRule, AddSuperUser, \
    SendSignNotice



urlpatterns = [
    url(r'getqrcode/',GetQrcode.as_view()),
    url(r'host_list/', HostList.as_view()),
    url(r'is_login/', IsLogin.as_view()),
    url(r'is-uuid-login/', IsUuidLogin.as_view()),
    url(r'push_product', PostGoods.as_view()),
    url(r'reset_heart_beat', ResetHeartBeat.as_view()),
    url(r'reset_single', ResetSingleHeartBeat.as_view()),
    url(r'define_sign_rule', DefineSignRule.as_view()),
    url(r'add_super_user', AddSuperUser.as_view()),
    url(r'send_signin_notice', SendSignNotice.as_view())
]



