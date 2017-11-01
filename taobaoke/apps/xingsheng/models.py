# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Product(models.Model):
    type = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now=True)
    # 包含文字*n，图片*n
    # '{img1: "http://www.xxx", text1: "xxxxx", "img2": "http://xxxxx", "img3": "http://xxx"}'
    desc = models.TextField()
    push_time = models.DateTimeField(default=None, null=True)
