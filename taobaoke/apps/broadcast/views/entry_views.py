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

import logging
logger = logging.getLogger('entry_views')



@csrf_exempt
def search_product(request):
    req_dict = json.loads(request.body)

    """
    由BotService筛选出keyword
    那么，这个请求就必然也是BotSercvice发起的。在哪儿发起？
    """
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

        """
        发送给BotService，处理函数位于tbk>views>tbk_agent_views.py
        """
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

