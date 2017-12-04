# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib import admin

from account.views.order_views import GetGoodPv, OrderList, OrderCommisionView, PostingAccount, SetBackUpInfoView, InviterLastLoginView, InviterOrderListView
from account.views.agent_views import GetCommision, AlipayAccountView, BindingAlipayAccountView, UserAvatarView

from broadcast.views.entry_views import insert_product
from broadcast.views.user_views import update_adzone, get_adzone_info, get_tkuser_info, \
    get_login_qrcode, poster_url, get_invite_code, GetPushTIme, SetPushTime
from broadcast.views.taobaoke_views import PushProduct, AcceptSearchView, ProductDetail, AppSearchDetailView, \
    AppSearchListView
from broadcast.views.operating_views import GetProducts, EditProduct
from user_auth.views import LoginView, RegisterVIew, SendTextMessage, ResetPassword, Logout


user_urls = [
    url(r'^update-adzone/', update_adzone),
    url(r'^get-adzone-info/', get_adzone_info),
    url(r'^get-tkuser-info/', get_tkuser_info),
    url(r'^get-invite-code/', get_invite_code),
    url(r'^poster/', poster_url)
]
## 新增了获取邀请码的接口,用于poster生成海报


product_urls = [
    url(r'insert/', insert_product),
    url(r'qrcode/', get_login_qrcode),
    url(r'detail/', ProductDetail.as_view()),

    url(r'search_list', AppSearchListView.as_view()),
    url(r'search_detail', AppSearchDetailView.as_view())
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
    url(r'^user-avatar/$', UserAvatarView.as_view()) #ok
]



tk_urls = [
    url(r'push_product', PushProduct.as_view()),
    url(r'search_product', AcceptSearchView.as_view()),
    url(r'set_pushtime', SetPushTime.as_view()),
    url(r'get_pushtime', GetPushTIme.as_view())
]

auth_urls = [
    url(r'login/$', LoginView.as_view()),
    url(r'register/$', RegisterVIew.as_view()),
    url(r'send_verifyNum/$', SendTextMessage.as_view()),
    url(r'reset/$', ResetPassword.as_view()),
    url(r'logout/$', Logout.as_view())
]

operating_urls = [
    url(r'operating/$', GetProducts.as_view()),
    url(r'operating-edit/$', EditProduct.as_view()),
]

urlpatterns = [
    url(r'product/', include(product_urls)),
    url(r'user/', include(user_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'tk', include(tk_urls)),
    url(r'auth/', include(auth_urls)),
    url(r'account/', include('account.urls')),
    url(r'operate/', include(operating_urls)),
]

