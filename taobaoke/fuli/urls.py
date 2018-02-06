# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib import admin

from account.views.order_views import GetGoodPv, OrderList, OrderCommisionView, PostingAccount, SetBackUpInfoView, \
    InviterLastLoginView, InviterOrderListView
from account.views.agent_views import GetCommision, AlipayAccountView, BindingAlipayAccountView, UserAvatarView

from broadcast.views.entry_views import insert_product
from broadcast.views.user_views import update_adzone, get_adzone_info, get_tkuser_info, \
    get_login_qrcode, poster_url, get_invite_code, GetPushTIme, SetPushTime,get_openid, get_update_qrcode, UserAutoPush
from broadcast.views.taobaoke_views import PushProduct, AcceptSearchView, ProductDetail_, AppSearchDetailView, \
    AppSearchListView, SendArtificialMsg, RecommendProduct, SelectProducts, PushCertainProduct, get_handle_pushtime, SendCaiGameProduct
from broadcast.views.operating_views import GetProducts, EditProduct, ChangePushStatus, RefreshProducts, DeleteProductImg, \
    ParseImg, SelectCate, QueryOrder

from user_auth.views import LoginView, RegisterVIew, SendTextMessage, ResetPassword, Logout, JudgeIsAgreeStatement

from mini_program.views.wishwall_views import WishWallView, AddFavoriteWish

from mini_program.views.card_views import CardViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"card", CardViewSet)


user_urls = [
    url(r'^update-adzone/', update_adzone),
    url(r'^get-adzone-info/', get_adzone_info),
    url(r'^get-tkuser-info/', get_tkuser_info),
    url(r'^get-invite-code/', get_invite_code),
    url(r'^poster/', poster_url),
    url(r'^get-openid/', get_openid),
    url(r'^get-chatqrcode/', get_update_qrcode),
    url(r'^get-handle-pushtime/', get_handle_pushtime),
    url(r'^auto-push/', UserAutoPush.as_view()),
]

product_urls = [
    url(r'insert/', insert_product),
    url(r'qrcode/', get_login_qrcode),
    url(r'detail/', ProductDetail_.as_view()),

    url(r'search_list', AppSearchListView.as_view()),
    url(r'search_detail', AppSearchDetailView.as_view()),
    url(r'recommand_product', RecommendProduct.as_view()),
    url(r'select-products', SelectProducts.as_view()),
    url(r'push-certain-product', PushCertainProduct.as_view()),

]

account_urls = [
    url(r'^good-pv/$', GetGoodPv.as_view()),
    url(r'^order-list/$', OrderList.as_view()),
    url(r'^order-commision/$', OrderCommisionView.as_view()),
    url(r'^inviter-order-list/$', InviterOrderListView.as_view()),
    url(r'^get-commision/$',GetCommision.as_view()),
    url(r'^inviter-last-login/$', InviterLastLoginView.as_view()),
    url(r'^set-backup-info/$', SetBackUpInfoView.as_view()),
    url(r'^bind-alipay/$',BindingAlipayAccountView.as_view()),
    url(r'^user-alipay/$', AlipayAccountView.as_view()),
    url(r'^user-avatar/$', UserAvatarView.as_view())
]



tk_urls = [
    url(r'push_product', PushProduct.as_view()),
    url(r'search_product', AcceptSearchView.as_view()),
    url(r'set_pushtime', SetPushTime.as_view()),
    url(r'get_pushtime', GetPushTIme.as_view()),

    url(r'send_artifical_msg', SendArtificialMsg.as_view()),
    url(r'send_caigame_product', SendCaiGameProduct.as_view()),
]

auth_urls = [
    url(r'login/$', LoginView.as_view()),
    url(r'register/$', RegisterVIew.as_view()),
    url(r'send_verifyNum/$', SendTextMessage.as_view()),
    url(r'reset/$', ResetPassword.as_view()),
    url(r'logout/$', Logout.as_view()),
    url(r'is_agree_statement', JudgeIsAgreeStatement.as_view())
]

operate_urls = [
    url(r'operating/$', GetProducts.as_view()),
    url(r'operating-edit/$', EditProduct.as_view()),
    url(r'delete-product-img/$', DeleteProductImg.as_view()),
    url(r'change-push-status/$', ChangePushStatus.as_view()),
    url(r'refresh-products/$', RefreshProducts.as_view()),
    url(r'parse-img/$', ParseImg.as_view()),
    url(r'select-cate/$', SelectCate.as_view()),
    url(r'query-order/$', QueryOrder.as_view()),
]

wish_urls = [
    url(r'index', WishWallView.as_view()),
    url(r'add_fav', AddFavoriteWish.as_view())
]

test_urls = [
    # url(r'test_notify', TestPaymentNotifyView.as_view())
]


urlpatterns = [
    url(r'product/', include(product_urls)),
    url(r'user/', include(user_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'tk', include(tk_urls)),
    url(r'auth/', include(auth_urls)),
    url(r'account/', include(account_urls)),
    url(r'operate/', include(operate_urls)),

    url(r'wish', include(wish_urls)),
    url(r'card/', include(router.urls))
]

