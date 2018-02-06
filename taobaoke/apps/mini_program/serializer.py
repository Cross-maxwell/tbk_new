# -*- coding: utf-8 -*-
# @Author: SmartKeyerror
# @Date  : 18-1-12 上午10:50

from rest_framework import serializers
from mini_program.models.wishwall_models import WishWall
from mini_program.models.card_models import Card


class WishWallModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishWall
        fields = "__all__"


class CardSerializers(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = "__all__"