from django.conf.urls import url
from django.contrib import admin
from user_auth.views import LoginView, RegisterVIew, SendTextMessage, ResetPassword, Logout

urlpatterns = [
    url(r'login/$', LoginView.as_view()),
    url(r'register/$', RegisterVIew.as_view()),
    url(r'send_verifyNum/$', SendTextMessage.as_view()),
    url(r'reset/$', ResetPassword.as_view()),
    url(r'logout/$', Logout.as_view())
]