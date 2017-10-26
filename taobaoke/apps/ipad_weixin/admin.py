# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from ipad_weixin.models import ChatRoom, WxUser, SignInRule


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('username', 'nickname', 'member_nums')


class WxUserAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'username', 'login', 'last_heart_beat')


class SignRuleAdmin(admin.ModelAdmin):
    exclude = ('red_packet_id',)



admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(WxUser, WxUserAdmin)
admin.site.register(SignInRule)