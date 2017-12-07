# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.test import TestCase
from django.test import Client
import requests

# Create your tests here.


class UserAuthTest(TestCase):

    def test_register(self):
        data = {
            "username": "chengzi",
            "password1": "123456",
            "password2": "123456",
            "verifyNum": "6562",
        }
        url = "http://localhost:9090/api/auth/register/"
        response = requests.post(url, data=json.dumps(data))
        print response.content

    def test_login(self):
        login_data = {
            "username": "smart",
            "password": "123456"
        }
        url = "http://localhost:9090/api/auth/login/"
        response = requests.post(url, data=json.dumps(login_data))
        print response.content

    def test_right_login(self):
        """
        登录接口测试
        """
        # 前端传入数据
        right_login_data = {
            "username": "test",
            "password": "123456"
        }
        # 线上域名为 http://s-pro-07.qunzhu666.com:9090
        # 访问url
        url = "http://localhost:9090/api/auth/login/"
        response = requests.post(url, data=json.dumps(right_login_data))
        print response.content
        """
        登录成功返回结果
        {"username": "test", "user_id": 4, "data": "\u767b\u5f55\u6210\u529f", "ret": 1}
        """