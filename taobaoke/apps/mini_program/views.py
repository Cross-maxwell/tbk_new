# -*- coding: utf-8 -*-
import json
from rest_framework.generics import ListCreateAPIView
from django.views.generic.base import View
from django.http import HttpResponse
from django.core import serializers
from rest_framework.views import APIView

from mini_program.serializer import WishWallModelSerializer
from mini_program.models import WishWall

import logging
logger = logging.getLogger('django_views')


class WishWallView(ListCreateAPIView):
    """
    Create or List wish_wall
    """
    serializer_class = WishWallModelSerializer

    def get_queryset(self):
        id = self.request.query_params.get("id", "")
        if id:
            return WishWall.objects.filter(id=id)
        return WishWall.objects.all().order_by('-created')


class AddFavoriteWish(View):
    def post(self, request):
        req_dict = json.loads(request.body)
        wish_id = req_dict.get("wish_id", "")
        if not wish_id:
            return HttpResponse(json.dumps({"ret": 0, "data": "参数缺失"}), status=400)
        wish_wall = WishWall.objects.get(id=wish_id)
        wish_wall.fav_num += 1
        wish_wall.save()
        serializer = WishWallModelSerializer(wish_wall)
        return HttpResponse(json.dumps(serializer.data), status=200)


class TestPaymentNotifyView(View):
    def post(self, request):
        logger.info("回调地址数据: {}".format(request.body))
        return HttpResponse(json.dumps({"ret": 1}))

