# -*- coding: utf-8 -*-
from rest_framework.generics import ListCreateAPIView

from mini_program.serializer import WishWallModelSerializer
from mini_program.models.wishwall_models import WishWall

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


