# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from account.views.order_views import GetGoodPv, OrderList, OrderCommisionView, PostingAccount, SetBackUpInfoView, \
    InviterLastLoginView, InviterOrderListView
from account.views.agent_views import GetCommission, AlipayAccountView, BindingAlipayAccountView
# setPushTimeView, getPushTimeView

account_urls = [

    ''' order_views.py '''

    url(r'^good-pv', GetGoodPv.as_view()),
    url(r'^order-list', OrderList.as_view()),
    url(r'^order-commission', OrderCommisionView.as_view())
    url(r'^inviter-order-list', InviterOrderListView.as_view()),
    url(r'^inviter-last-login', InviterLastLoginView.as_view()),
    # 设置二级代理备注
    url(r'^set-backup-info', SetBackUpInfoView.as_view()),
    # PostingAccount.as_view()


    ''' agent_views.py '''
    #绑定支付宝帐号
    url(r'^user-alipay', AlipayAccountView.as_view()),
    url(r'^bind-alipay',BindingAlipayAccountView.as_view()),
    url(r'^get-commission',GetCommission.as_view()),
    # # 查询时间段内新增人数
    # url(r'^new-tk', NewUserCount.as_view()),
    # url(r'^check-userconfig', CheckAllUserConfig.as_view()),

    # url(r'^get-pushtime', getPushTimeView.as_view()),
    # 发单群--设置发单时间
    # url(r'^set-pushtime', setPushTimeView.as_view()),


    '''' poster_view.py '''
    # url(r'^poster/$', poster_url),
    # url(r'^poster/checkin$', checkin_poster_url),


    # # "我",资料页
    # url(r'^user/avatar', bot_api.rest_auth.views.UserAvatarView.as_view()),


    # 以下未知- -暂不启用
]


    ## 停用
    # url(r'^amount', AmountView.as_view()),
    # # 查询用户是否开通了 商品搜索功能
    # url(r'^check-search', is_search_func_openned),
    # url(r'^init-commision', InitCommisionView.as_view()),
    # url(r'^rf-allgroup', refreshAllGroup.as_view()),
    # url(r'^is-push', is_push),
    # url(r'^cal-commission', AutoCalCommisionView.as_view()),