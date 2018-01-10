# -*- coding: utf-8 -*-

from rest_framework import serializers
from mini_program.models.wishwall_models import WishWall
from mini_program.models.payment_models import UserAddress, PaymentOrder


class WishWallModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishWall
        fields = "__all__"


class AppUserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = "__all__"


class PaymentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = "__all__"