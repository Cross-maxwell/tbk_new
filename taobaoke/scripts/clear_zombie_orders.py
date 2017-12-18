# coding: utf-8
"""
用于清理两个月没结算的订单, 将其失效
"""

import sys
sys.path.append('/home/new_taobaoke/taobaoke')

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from account.models.order_models import Order
from datetime import datetime, timedelta
from django.utils import timezone


# Users that had never logged in in last three months.
forgotten_orders = Order.objects.filter(order_status='订单付款', create_time__lte=timezone.now()-timedelta(weeks=8))

for o in forgotten_orders:
    o.order_status = '订单失效'
    o.save()

