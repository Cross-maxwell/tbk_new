# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import random
import re
import time
import datetime
import requests

from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from broadcast.models.entry_models import Product, PushRecord
from broadcast.models.user_models import TkUser


import logging
logger = logging.getLogger('entry_views')

@csrf_exempt
def insert_product(request):
    req_dict = json.loads(request.body)

    key_list = [
        'title', 'desc', 'img_url',
        'cupon_value', 'price', 'cupon_url',
        'sold_qty', 'cupon_left',
    ]
    item_id = re.search('itemId=(\d+)', req_dict['cupon_url']).groups()[0]
    if Product.objects.filter(item_id=item_id).exists():
        p = Product.objects.get(item_id=item_id)
        for key in key_list:
            setattr(p, key, req_dict[key])
        if req_dict['is_finished'] == 'true' or req_dict['cupon_left'] == 0:
            p.available = False
        else:
            p.available = True
        p.save()
        logger.info('Product updated.')
    else:
        p = Product.objects.create(**{key: req_dict[key] for key in key_list})
    p.refresh_from_db()
    p.assert_available()

    return HttpResponse('Success', status=201)

@csrf_exempt
def push_product(request):
    data = {
        "ret_code": 0,
        "reaction_list": [
        ]
    }
    request_data = json.loads(request.body)
    group_id = request_data['gid']
    host_id = request_data['hid']
    # pid = request_data['pid']
    username = request_data['username']
    push_url = request_data.get('post_url', 'http://s-prod-07.qunzhu666.com:8000/api/platform-api/create-exec/')
    tk_user = TkUser.get_user(username)
    pid = tk_user.adzone.pid

    begin_time = datetime.datetime.strptime(request_data['begin_time'].replace('24:00', '23:59'), '%H:%M')
    end_time = datetime.datetime.strptime(request_data['end_time'].replace('24:00', '23:59'), '%H:%M')

    if not begin_time.time() < datetime.datetime.now().time() < end_time.time():
        data['ret_code'] = -1
        return HttpResponse(json.dumps(data), status=200)

    qs = Product.objects.filter(
        ~Q(pushrecord__group__contains=group_id, pushrecord__create_time__gt=timezone.now() - datetime.timedelta(days=3)),
        available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
    )

    # 用发送过的随机商品替代
    if qs.count() == 0:
        qs = Product.objects.filter(
            available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
        )
        requests.post(
            'https://hook.bearychat.com/=bw8NI/incoming/219689cd1075dbb9b848e4c763d88de0',
            json={'text': '点金推送商品失败：无可用商品, group_id=%s' % group_id}
        )

    for _ in range(50):
        try:
            r = random.randint(0, qs.count() - 1)
            p = qs.all()[r]
            break
        except Exception as exc:
            print "Get entry exception. Count=%d." % qs.count()
            print exc.message

    img_msg = {
        'type': 'img',
        'content': p.get_img_msg(),
        'host_id': host_id,
        'target_id': group_id,
    }

    text_msg = {
        'type': 'text',
        'content': p.get_text_msg(pid),
        'host_id': host_id,
        'target_id': group_id,
    }

    PushRecord.objects.create(entry=p, group=group_id)

    requests.post(push_url, json.dumps(img_msg))
    print "Push img %s to group %s." % (img_msg['content'], img_msg['target_id'])
    # time.sleep(5)
    requests.post(push_url, json.dumps(text_msg))
    print "Push text %s to group %s." % (text_msg['content'], text_msg['target_id'])
    return HttpResponse(json.dumps(data), status=200)
