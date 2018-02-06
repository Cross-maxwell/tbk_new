# -*- coding: utf-8 -*-
# @Author: SmartKeyerror
# @Date  : 18-2-6 上午10:05


from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from mini_program.serializer import CardSerializers
from mini_program.models.card_models import Card


class CardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


class CardViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Card.objects.all().order_by('-date')
    serializer_class = CardSerializers
    pagination_class = CardPagination

