# -*- coding:utf-8 -*-
from django.http import HttpResponse
from xingsheng.models import Product
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
import json

import logging
logger = logging.getLogger('django_views')

class AcceptProductView(View):
    @csrf_exempt
    def post(self, request):
        user = request.user
        product_data = json.loads(request.body)
        # 目前有种类型的商品，1为即时推送，2为定时推送.
        product_type = product_data.get("type", "")
        data_dict = product_data.get("data", "")
        if data_dict:
            json_data = json.dumps(data_dict)
            try:
                Product.objects.create(type=product_type, desc=json_data)
            except Exception as e:
                logger.error(e)
        return HttpResponse(json.dumps({"ret": "1", "data": "商品添加成功"}))


class ProcessProduct(View):
    def get(self, request):
        # 首先处理type为1的商品
        high_product_list = Product.objects.first(type="1").all()
        for high_product in high_product_list:
            data = json.loads(high_product).get("data")
            for item in data:
                if "img" in data:
                    pass






"""
{
    "type":
    "data":{
        "img1": "",
        "text1": "",
        "img2": "",
        "img3": ""
    },
    "push_time": "10:00"
}
"""
