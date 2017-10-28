# _*_ coding:utf-8 _*_
from rest_framework import serializers
from account.models.commision_models import AlipayAccount, Commision


class AlipayAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlipayAccount
        fields = ('alipay_id', 'alipay_name', 'identity_num', 'phone_num')


class CommisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commision
        fields = ('balance', 'sum_earning_amount', 'sum_payed_amount', 'is_valid', 'commision_rate')
