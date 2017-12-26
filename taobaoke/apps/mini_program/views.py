# -*- coding: utf-8 -*-
import json
from rest_framework.generics import ListCreateAPIView
from django.views.generic.base import View
from django.http import HttpResponse

from mini_program.serializer import WishWallModelSerializer
from mini_program.models import WishWall

import logging
logger = logging.getLogger('django_views')


class WishWallView(ListCreateAPIView):
    """
    Create or List wish_wall
    """
    queryset = WishWall.objects.all()
    serializer_class = WishWallModelSerializer

    def get_queryset(self):
        return WishWall.objects.all().order_by('-created')


class TestPaymentNotifyView(View):
    def post(self, request):
        logger.info("回调地址数据: {}".format(request.body))
        return HttpResponse(json.dumps({"ret": 1}))

