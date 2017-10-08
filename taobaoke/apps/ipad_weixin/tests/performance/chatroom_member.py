# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
import json
import random
import time

from ipad_weixin.models import Message, WxUser, Contact, Qrcode, Img, ChatRoom, GroupMembers

class TestChatroomMemberPerformance(TestCase):
    def test_chatroom_member_performance(self):
        cr = ChatRoom.objects.create()
        cr.username = '1'
        for i in range(100):
            gm = GroupMembers.objects.create()
            gm.username = str(i)
            gm.chatroom.add(cr)
            gm.save()
        cr.save()
        for j in range(50):
            print time.time()
            cr.groupmembers_set.remove(gm)
            cr.save()
            print time.time()
