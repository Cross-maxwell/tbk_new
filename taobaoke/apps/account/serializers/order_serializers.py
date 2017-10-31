# coding=utf-8
from account.models.order_models import Order


# import rest_framework.serializers as drf_serializers
from rest_framework import serializers

class OrderSerializer(serializers.ModelSerializer):
    earning_time = serializers.CharField(   allow_blank=True, required=False )


    # 佣金金额
    commision_amount = serializers.FloatField(write_only=True)
    # 佣金比率
    commision_rate = serializers.CharField(write_only=True)

    # 显示佣金比率
    show_commision_rate = serializers.CharField(read_only=True,source='get_show_commision_rate')
    # 显示佣金金额
    show_commision_amount = serializers.FloatField(read_only=True,source='get_show_commision_amount')



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
