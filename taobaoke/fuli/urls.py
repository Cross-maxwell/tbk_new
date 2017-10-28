# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib import admin
from broadcast.views.entry_views import insert_broadcast_by_msg, insert_product_by_msg, insert_product, search_product, push_product, search_product_pad
from broadcast.views.user_views import update_adzone, get_adzone_info, get_tkuser_info, get_login_qrcode
from account.views.order_views import GetGoodPv, OrderList, OrderCommisionView, PostingAccount, SetBackUpInfoView, InviterLastLoginView, InviterOrderListView
from account.views.agent_views import GetCommision, AlipayAccountView, BindingAlipayAccountView, UserAvatarView

from broadcast.views.entry_views import insert_broadcast_by_msg, insert_product_by_msg, \
    insert_product, search_product, push_product, search_product_pad
from broadcast.views.user_views import update_adzone, get_adzone_info, get_tkuser_info, \
    get_login_qrcode
from ipad_weixin.views.base_views import GetQrcode, HostList, IsUuidLogin, IsLogin, \
    DefineSignRule, AddSuperUser, ResetSingleHeartBeat, ResetHeartBeat
from broadcast.views.taobaoke_views import PostGoods, SendSignNotice, SetPushTime
from user_auth.views import LoginView, RegisterVIew, SendTextMessage, ResetPassword, Logout


user_urls = [
    url(r'^update-adzone/', update_adzone),
    url(r'^get-adzone-info/', get_adzone_info),
    url(r'^get-tkuser-info/', get_tkuser_info),
]

product_urls = [
    url(r'insert/', insert_product),
    url(r'insert-by-msg/', insert_product_by_msg),
    url(r'qrcode/', get_login_qrcode),
]

interact_urls = [
    url(r'search-product/', search_product),
    url(r'search-product-pad/', search_product_pad),
    url(r'push-product/', push_product),
]

broadcast_urls = [
    url(r'insert/', insert_broadcast_by_msg),
    url(r'push/', insert_broadcast_by_msg),
]

account_urls = [
    url(r'^good-pv/$', GetGoodPv.as_view()),#ok
    url(r'^order-list/$', OrderList.as_view()), #ok
    url(r'^order-commision/$', OrderCommisionView.as_view()), #ok
    url(r'^inviter-order-list/$', InviterOrderListView.as_view()), #ok
    url(r'^get-commision/$',GetCommision.as_view()), #ok
    url(r'^inviter-last-login/$', InviterLastLoginView.as_view()),#ok
    url(r'^set-backup-info/$', SetBackUpInfoView.as_view()), #ok
    url(r'^bind-alipay/$',BindingAlipayAccountView.as_view()), #ok
    url(r'^user-alipay/$', AlipayAccountView.as_view()),#ok
    url(r'^user-avatar', UserAvatarView.as_view()) #ok
]


robot_urls = [
    url(r'getqrcode/', GetQrcode.as_view()),
    url(r'host_list/', HostList.as_view()),
    url(r'is_login/', IsLogin.as_view()),
    url(r'is_uuid_login/', IsUuidLogin.as_view()),
    url(r'define_sign_rule', DefineSignRule.as_view()),
    url(r'add_super_user', AddSuperUser.as_view()),

    url(r'reset_heart_beat', ResetHeartBeat.as_view()),
    url(r'reset_single', ResetSingleHeartBeat.as_view()),
]

tk_urls = [
    url(r'push_product', PostGoods.as_view()),
    url(r'send_signin_notice', SendSignNotice.as_view()),
    url(r'set_pushtime', SetPushTime.as_view())
]

auth_urls = [
    url(r'login/$', LoginView.as_view()),
    url(r'register/$', RegisterVIew.as_view()),
    url(r'send_verifyNum/$', SendTextMessage.as_view()),
    url(r'reset/$', ResetPassword.as_view()),
    url(r'logout/$', Logout.as_view())
]


urlpatterns = [
    url(r'product/', include(product_urls)),
    url(r'^user/', include(user_urls)),
    url(r'interact/', include(interact_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'broadcast/', include(broadcast_urls)),

    url(r'robot/', include(robot_urls)),
    url(r'tk', include(tk_urls)),
    url(r'auth/', include(auth_urls)),

    url(r'account/', include('account.urls'))
]

