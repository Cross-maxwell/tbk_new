# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase

from .models import Message, WxUser, Contact, Qrcode, Img


"""
一个非常简单的测试案例
"""
# class QrcodeTest(TestCase):
#     def setUp(self):
#         print 'start test'
#
#     def test_save_qrcode(self):
#         dict = {}
#         Qrcode.save_qr_code(dict)
#
#     def tearDown(self):
#         print 'end test'

class SaveQrcodeTest(TestCase):
    def test_update_qr_code(self):
        qr_code_db = Qrcode.objects.filter(id=4)
        dict = {u'Status': 2,
                u'Username': u'wxid_9zoigugzqipj21',
                u'CheckTime': 0,
                u'HeadImgUrl': u'http://wx.qlogo.cn/mmhead/ver_1/oStSdNJuRT3qQ9c2bf9icIPGXp4flIic2FouS0hZqvdiaD30PxDlQPdAnbeIZpicMGBRkxbIUm7SyMpvaBdCyIDsnP1Niavl21eEoTToicbOUmeHY/0',
                u'Uuid': u'',
                u'NotifyKey': None,
                u'ExpiredTime': 0,
                u'ImgBuf': None,
                u'RandomKey': u'UHWAVQI3tH6NXbnccI4PgA==',
                u'Password': u'extdevnewpwd_CiNBUWJTeldRWjhhN0VqamRFUTU1TVgzZU9AcXJ0aWNrZXRfMBJAZkg0bXdNZ1F2a191RmI5Q1g0Wk84T0tOQjFsTUlOaWQ2MlN1b1hDWkwtNi0zU0w1SmhlWVZXWXdTdklJV2FNcRoYZ1NmQTZOMXR1SGxxNWdDRG5pU2twMFpE',
                u'Nickname': u'\u964c'
                }
        Qrcode.update_qr_code(dict, qr_code_db)

