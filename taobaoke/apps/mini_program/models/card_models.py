# -*- coding: utf-8 -*-
# @Author: SmartKeyerror
# @Date  : 18-2-6 上午10:02

from django.db import models


class Card(models.Model):
    username = models.CharField(max_length=64)
    head_url = models.URLField(max_length=500)
    bg_url = models.URLField(max_length=500)
    text = models.TextField(default="")

    date = models.DateTimeField(auto_now_add=True)

