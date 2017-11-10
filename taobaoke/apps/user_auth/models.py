# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PushTime(models.Model):
    user = models.OneToOneField(User)
    # 发单间隔
    interval_time = models.CharField(max_length=20, default=5)
    # 每天开始时间
    begin_time = models.CharField(max_length=20, default="07:00")
    # 每天停止时间
    end_time = models.CharField(max_length=20, default='23:00')

    is_valid = models.BooleanField(default=True)
    update_time = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.update_time = timezone.now()
        return super(PushTime, self).save(*args, **kwargs)

    def get_pushtime(self, md_username):
        try:
            pushtime = PushTime.objects.get(user__username=md_username)
        except Exception as e:
            pushtime = PushTime()
            pushtime.user = User.objects.get(username=md_username)
            pushtime.save()
        return pushtime


@receiver(post_save, sender=User)
def create_pushtime(sender, instance, created, **kwargs):
    if created:
        PushTime.objects.create(user=instance)

