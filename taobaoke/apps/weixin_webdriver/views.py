# -*- coding: utf-8 -*-
from weixin_webdriver.bot import WebDriverBot
from django.views.generic.base import View
from django.http import HttpResponse
import json

class LoginQrcode(View):
    """
    接口： http://s-prod-04.qunzhu666.com:8080/webdriver/getqrcode
    """
    def get(self, request):
        user = request.user
        webdriver = WebDriverBot(user=user)
        qrcode = webdriver.get_qrcode()
        webdriver.run()

        return HttpResponse(json.dumps({"login_url": 'https://login.weixin.qq.com/l/' + qrcode}))



