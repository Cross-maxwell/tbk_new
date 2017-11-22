# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from models.order_models import Order
from django.contrib.auth.models import User


class OrderAdmin(admin.ModelAdmin):

    list_display = ('good_info','user_id','status_orders')
    search_fields = ('good_info','=user_id','=ad_id',)
    list_filter = ('order_status','enter_account')

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(OrderAdmin,self).get_search_results(request, queryset, search_term)
        try:
            user = User.objects.filter(username=search_term).first()
            if user:
                userid = str(int(user.id))
                queryset |= self.model.objects.filter(user_id=userid)
        except:
            pass
        return queryset, use_distinct


admin.site.register(Order,OrderAdmin)