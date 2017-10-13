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


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        md_username = '12345'

        wx_bot = WXBot()
        (oss_path, qrcode_rsp, deviceId) = wx_bot.get_qrcode(md_username)

        try:
            buffers = qrcode_rsp.baseMsg.payloads
            qr_code = json.loads(buffers)
            uuid = qr_code['Uuid']
            qr_code_db = Qrcode.objects.filter(uuid=uuid).order_by('-id').first()
            qr_code_db.md_username = md_username
            qr_code_db.save()
        except Exception as e:
            print(e)

        import thread

        thread.start_new_thread(wx_bot.check_and_confirm_and_load, (qrcode_rsp, deviceId))

        time.sleep(10)