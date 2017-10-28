from django.conf.urls import url
from account.views.order_views import GetGoodPv, OrderList, OrderCommisionView, PostingAccount, SetBackUpInfoView, InviterLastLoginView, InviterOrderListView
from account.views.agent_views import GetCommision, AlipayAccountView, BindingAlipayAccountView

urlpatterns = [
    url(r'^good-pv/$', GetGoodPv.as_view()),#ok
    url(r'^order-list/$', OrderList.as_view()), #ok
    url(r'^order-commision/$', OrderCommisionView.as_view()), #ok
    url(r'^inviter-order-list/$', InviterOrderListView.as_view()), #ok
    url(r'^get-commision/$',GetCommision.as_view()), #ok
    url(r'^inviter-last-login/$', InviterLastLoginView.as_view()),#ok
    url(r'^set-backup-info/$', SetBackUpInfoView.as_view()),
    url(r'^bind-alipay/$',BindingAlipayAccountView.as_view()),
    url(r'^user-alipay/$', AlipayAccountView.as_view())
]