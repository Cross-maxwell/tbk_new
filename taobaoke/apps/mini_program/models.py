# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

# Create your models here.


class WishWall(models.Model):
    username = models.CharField(max_length=100)
    img_url = models.CharField(max_length=500, null=True, blank=True)
    wish_content = models.TextField()
    font_img = models.CharField(max_length=500, default='', null=True, blank=True)
    created = models.DateTimeField(auto_now=True)

