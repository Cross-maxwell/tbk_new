# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError

import json
import time
from broadcast.models.user_models import TkUser
from django.http import HttpResponse
from django.views.generic.base import View

from ipad_weixin.weixin_bot import WXBot
from ipad_weixin.models import Qrcode, WxUser, ChatRoom
from ipad_weixin.heartbeat_manager import HeartBeatManager


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        auth_users = WxUser.objects.all()
        for auth_user in auth_users:
            HeartBeatManager.begin_heartbeat(auth_user.username)
