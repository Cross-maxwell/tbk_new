# coding=utf-8
from account.models.order_models import Order
from rest_framework import serializers

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
             'id', 'create_time', 'click_time','good_info','good_id',
             'wangwang', 'shop', 'good_num','good_price','order_status',
             'order_type', 'earning_rate', 'share_rate','pay_amount','result_predict',
             'balance_amount', 'money_amount', 'earning_time','good_info','commision_rate',
             'commision_amount','show_commision_amount','show_commision_rate',
             'subsidy_rate', 'subsidy_amount', 'subsidy_type','terminalType','third_service',
             'order_id', 'category_name', 'source_id','source_media','ad_id','ad_name',
             'last_update_time','enter_account'
        )
