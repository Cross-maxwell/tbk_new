from django.conf.urls import url

from broadcast.views.taobaoke_views import PostGoods, SendSignNotice

urlpatterns = [
    url(r'push_product', PostGoods.as_view()),
    url(r'send_signin_notice', SendSignNotice.as_view())
]