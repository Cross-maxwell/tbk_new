# -*- coding: utf-8 -*-
from rest_framework.generics import ListCreateAPIView

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


# class WishWallView(View):
#     """
#     使用Django原生View， 和上面对比差异非常明显
#     """
#     def get(self, request):
#         try:
#             wish_wall = WishWall.objects.all()
#             json_data = serializers.serialize("json", wish_wall)
#             return HttpResponse(json_data, content_type="application/json")
#         except Exception as e:
#             logger.error(e)
#             return HttpResponse(json.dumps({"ret": 0}), status=500)
#     def post(self, request):
#         req_data = json.loads(request.body)
#         try:
#             WishWall.objects.create(**req_data)
#             return HttpResponse(json.dumps({"ret": 1, "data": "添加成功"}), status=200)
#         except Exception as e:
#             logger.error(e)
#             return HttpResponse(json.dumps({"ret": 0}), status=500)


