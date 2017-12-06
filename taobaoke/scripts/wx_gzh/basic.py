# -*- coding: utf-8 -*-
import urllib
import time
import json
import sys
# sys.path.append('/root/project/new_taobaoke/taobaoke')
sys.path.append('/root/project/new_taobaoke/taobaoke')
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()
from fuli import top_settings
from django.core.cache import cache

openid = 'oo-aE1ghNVTBShFhW-vRHeaRH72Q'
TEMPLATE_ID = '0g9k7JY2qBjJO1aLIiJap7WWLMw7FvvLpT7BrnEui5E'
MMT_URL = 'http://tmp.zhiqun365.com/robot/robotlist'
GZH_ACESS_KEY = 'gzh_acess_key'

class Basic:
    accessToken = ''

    def __init__(self):
        self.__accessToken = ''
        self.__leftTime = 0

    def __real_get_access_token(self):

        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="
                   "client_credential&appid=%s&secret=%s" % (top_settings.APPID, top_settings.APPSECRET))
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        self.__accessToken = urlResp['access_token']
        Basic.accessToken = urlResp['access_token']
        cache.set(GZH_ACESS_KEY, urlResp['access_token'], 2*60 * 60)
        print 'Basic.accessToken:' + Basic.accessToken
        self.__leftTime = urlResp['expires_in']

    def get_access_token(self):
        if self.__leftTime < 10:
            self.__real_get_access_token()
        return self.__accessToken

    def run(self):
        while True:
            if self.__leftTime > 20:
                time.sleep(2)
                self.__leftTime -= 2
            else:
                self.__real_get_access_token()


if __name__ == '__main__':
    b = Basic()
    b.run()
