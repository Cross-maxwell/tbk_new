# coding=utf-8
import datetime
import json
import random
import time

import requests
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from broadcast.models import *


pid = 'mm_122190119_25238069_95116426'


def push_product(p, pid):

    PushRecord.objects.create(entry=p, group='qm')

    url = 'http://s-prod-01.qunzhu666.com/api/platform-api/create-exec/'
    # 福利社
    msg1 = {
        'type': 'img',
        'content': p.get_img_msg(),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '58facc29cae2280020ca49a8',
    }
    msg2 = {
        'type': 'text',
        'content': p.get_text_msg(pid=pid),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '58facc29cae2280020ca49a8',
    }

    msg3 = {
        'type': 'img',
        'content': p.get_img_msg(),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '59006ab23d1f250017b9d5f6',
    }
    msg4 = {
        'type': 'text',
        'content': p.get_text_msg(pid=pid),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '59006ab23d1f250017b9d5f6',
    }

    msg5 = {
        'type': 'img',
        'content': p.get_img_msg(),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '590d9919e16a9f0018cc6528',
    }
    msg6 = {
        'type': 'text',
        'content': p.get_text_msg(pid=pid),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '590d9919e16a9f0018cc6528',
    }
    # 大鸡
    msg11 = { 
        'type': 'img',
        'content': p.get_img_msg(),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '58f88aaf3d1f2500104a6ccd', 
    }
    msg12 = {
        'type': 'text',
        'content': p.get_text_msg(pid=pid),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '58f88aaf3d1f2500104a6ccd',
    }
    msg7 = { 
        'type': 'img',
        'content': p.get_img_msg(),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '5919771324ba9a0012b20223', 
    }
    msg8 = {
        'type': 'text',
        'content': p.get_text_msg(pid=pid),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '5919771324ba9a0012b20223',
    }
    # 电影
    msg9 = { 
        'type': 'img',
        'content': p.get_img_msg(),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '591a584c459914001f8df490', 
    }
    msg10 = {
        'type': 'text',
        'content': p.get_text_msg(pid=pid),
        'host_id': '58cfde0f498fad001bed0af2',
        'target_id': '591a584c459914001f8df490',
    }

    requests.post(url, json.dumps(msg1))
    requests.post(url, json.dumps(msg3))
    requests.post(url, json.dumps(msg5))
    requests.post(url, json.dumps(msg7))
    requests.post(url, json.dumps(msg9))
    requests.post(url, json.dumps(msg11))
    
    time.sleep(5)

    requests.post(url, json.dumps(msg2))
    requests.post(url, json.dumps(msg4))
    requests.post(url, json.dumps(msg6))
    requests.post(url, json.dumps(msg8))
    requests.post(url, json.dumps(msg10))
    requests.post(url, json.dumps(msg12))


class Command(BaseCommand):
    def handle(self, *args, **options):
        for _ in range(50):
            try:
                qs = Product.objects.filter(
                      ~Q(pushrecord__group__contains='qm'),
                      available=True,
                      last_update__gt=timezone.now() - datetime.timedelta(hours=4),
                    )
                success = False
                r = random.randint(0, qs.count())
                p = qs.all()[r]

                if not p.assert_available():
                    continue

                push_product(p, pid)
                success = True
                break
            except Exception as exc:
                print exc.message
        if not success:
            requests.post(
                'https://hook.bearychat.com/=bw8NI/incoming/219689cd1075dbb9b848e4c763d88de0',
                json={'text': '推送商品失败：无可用商品'}
            )
