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
from django.utils import timezone
import datetime

import logging
logger = logging.getLogger('weixin_bot')
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        auth_users = WxUser.objects.filter(last_heart_beat__gt=timezone.now() - datetime.timedelta(minutes=300))
        for auth_user in auth_users:
            logger.info("%s command 开启心跳" % auth_user.nickname)
            HeartBeatManager.begin_heartbeat(auth_user.username)

"""
2017-10-16 03:04:59.977565
"""