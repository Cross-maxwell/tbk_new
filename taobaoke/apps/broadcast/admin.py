# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from broadcast import models


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview',)

    def thumbnail_preview(self, obj):
        return '<img src="{url}" height=20px width=20px /> {title}'.format(url=obj.img_url, title=obj.title)

    thumbnail_preview.allow_tags = True
    thumbnail_preview.short_description = 'thumbnail'
