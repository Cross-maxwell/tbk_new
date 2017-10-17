# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import random
import re
import time
import datetime
import requests
from django.utils import timezone

import scrapy
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri
from django.views.decorators.csrf import csrf_exempt
from scrapy.crawler import CrawlerProcess
from django.db.models import Q

from broadcast.models.entry_models import Product, PushRecord
from broadcast.models.user_models import TkUser
from broadcast.management.commands.push import push_product
from broadcast.views.server_settings import *


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
        print 'Product updated.'
    else:
        p = Product.objects.create(**{key: req_dict[key] for key in key_list})
    p.refresh_from_db()
    p.assert_available()

    return HttpResponse('Success', status=201)


@csrf_exempt
def insert_product_by_msg(request):
    return HttpResponse('Success', status=201)


@csrf_exempt
def insert_broadcast_by_msg(request):
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




@csrf_exempt
def search_product(request):
    req_dict = json.loads(request.body)
    key_word = req_dict['keyword']
    try:
        username = req_dict['username']
        tku = TkUser.objects.get(user__username=username)
        text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
    %s""" % iri_to_uri(tku.get_search_url(key_word))
        rst_dict = {
            'ret_code': 1,
            'reaction_list': [
                {'type': 'text', 'content': text},
            ]
        }

    except:
        text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
    %s""" % iri_to_uri('http://s-prod-04.qunzhu666.com/hpt/index.php?action=search&q=' + key_word)
        rst_dict = {
            'ret_code': 1,
            'reaction_list': [
                {'type': 'text', 'content': text},
            ]
        }

    return HttpResponse(json.dumps(rst_dict))


@csrf_exempt
def search_product_pad(request):
    try:
        username = request.GET.get('username', '')
        uin = request.GET.get('uin', '')
        key_word = request.GET.get('keyword', '')
        gid = request.GET.get('gid', '')

        if username == '' or key_word == '' or gid == '' or uin == '':
            return HttpResponse("incorrect params,username:{0},keyword:{1}, gid:{2}"
                                .format(username, key_word, gid))

        r = requests.get("http://" + S_PROD_07_INT + "/api/tk/check-search?username={0}".format(username), timeout=10)
        if r.status_code != 200:
            return HttpResponse("remote server ret_code:{0} --{1}".format(r.status_code, r.text))
        ret_code = json.loads(json.loads(r.text))

        if ret_code['data'] != 1:
            return HttpResponse("check search fail:{0}".format(ret_code['data']))

        tku = TkUser.objects.get(user__username=username)
        text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
        {}""".format(iri_to_uri(tku.get_search_url(key_word)))

        params_dict = {
            "uin": uin,
            "group_id": gid,
            "text": text,
            "type": "text"
        }
        bot_request = requests.get("http://" + S_PROD_04_INT + ":5000/send_msg_type", params=params_dict, timeout=10)
        # print bot_request.url
        if bot_request.status_code != 200:
            return HttpResponse("error ret status:{0} from remote bot server--{1}"
                                .format(bot_request.status_code, bot_request.text))
        else:
            return HttpResponse("success")

    except Exception as e:
        return HttpResponse("exception occurred:{0}".format(e.message))
    # req_dict = json.loads(request.body)
    # key_word = req_dict['keyword']
    # try:
    #     username = req_dict['username']
    #     tku = TkUser.objects.get(user__username=username)
    #     text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
    # %s""" % iri_to_uri(tku.get_search_url(key_word))
    #     rst_dict = {
    #         'ret_code': 1,
    #         'reaction_list': [
    #             {'type': 'text', 'content': text},
    #         ]
    #     }
    #
    # except:
    #     text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
    # %s""" % iri_to_uri('http://s-prod-04.qunzhu666.com/hpt/index.php?action=search&q=' + key_word)
    #     rst_dict = {
    #         'ret_code': 1,
    #         'reaction_list': [
    #             {'type': 'text', 'content': text},
    #         ]
    #     }
    #
    # return HttpResponse(json.dumps(rst_dict))


def hijack_ll(request):
    keyword = request.GET.get('keyword')
    pid = request.GET.get('pid')
    resp = requests.get(
        url=iri_to_uri('http://chong2.xiaoshijie.com/saber/index/search?search=' + keyword)
    )
    content = resp.content.decode('utf-8')
    content = content.replace('mm_122190119_25238069_95116426', pid)
    return HttpResponse(content, content_type='charset=utf-8')
