# -*- coding: utf-8 -*-
import urllib
import time
import json

APPID = "wxb2a7ecf531203bba"
APPSECRET = "52adf580854e066d75f8d88ba96e0823"

openid = 'oo-aE1ghNVTBShFhW-vRHeaRH72Q'
TEMPLATE_ID = '0g9k7JY2qBjJO1aLIiJap7WWLMw7FvvLpT7BrnEui5E'
MMT_URL = 'http://tmp.zhiqun365.com/robot/robotlist'

class Basic:
    accessToken = ''

    def __init__(self):
        self.__accessToken = ''
        self.__leftTime = 0

    def __real_get_access_token(self):

        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="
                   "client_credential&appid=%s&secret=%s" % (APPID, APPSECRET))
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        self.__accessToken = urlResp['access_token']
        Basic.accessToken = urlResp['access_token']
        print 'Basic.accessToken:' + Basic.accessToken
        self.__leftTime = urlResp['expires_in']

    def get_access_token(self):
        if self.__leftTime < 10:
            self.__real_get_access_token()
        return self.__accessToken

    def run(self):
        while True:
            if self.__leftTime > 10:
                time.sleep(2)
                self.__leftTime -= 2
            else:
                self.__real_get_access_token()


if __name__ == '__main__':
    b = Basic()
    b.run()
