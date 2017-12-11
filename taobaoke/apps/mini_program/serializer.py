# -*- coding: utf-8 -*-

from rest_framework import serializers
from mini_program.models import WishWall


class WishWallModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishWall
        fields = "__all__"




