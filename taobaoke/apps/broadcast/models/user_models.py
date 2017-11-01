# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
from django.utils import timezone
import requests
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

import logging
logger = logging.getLogger('django_models')


class TkUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adzone = models.ForeignKey('Adzone', db_column='adzone_key', null=True)
    search_url_template = models.CharField(max_length=128, null=True)
    avatar_url = models.CharField(max_length=256, null=True, blank = True)
    inviter_id = models.CharField(max_length = 16, null=True)
    inviter_backup_info = models.CharField(max_length = 128, null=True)

    def get_adzone_id(self):
        return self.adzone.pid.split('_')[-1]

    def get_search_url(self, keyword):
        return unicode(self.search_url_template).format(keyword=keyword)

    def assign_pid(self):
        try:
            available_adzone = Adzone.objects.filter(tkuser=None)[0]
            self.adzone = available_adzone
        except Exception as exc:
            requests.post(
                'https://hook.bearychat.com/=bw8NI/incoming/ab2346561ad4c593ea5b9a439ceddcfc',
                json={'text': '分配PID出现异常. %s, username=%s' % (exc.message, self.user.username)}
            )

    def save(self, *args, **kwargs):
        if self.adzone is None:
            self.assign_pid()
        super(TkUser, self).save(*args, **kwargs)

    @classmethod
    def get_user(cls, username):
        try:
            tk_user = TkUser.objects.get(user__username=username)
            return tk_user
        except TkUser.DoesNotExist as exc:
            logger.error("用户尚未注册，开发人员调试时请确保auth_user已被创建")
            # user = User.objects.create_user(username=username)
            # return TkUser.objects.get(user=user)


@receiver(post_save, sender=User)
def create_tkuser(sender, instance, created, **kwargs):
    if created:
        TkUser.objects.create(user=instance, adzone=None)
    else:
        instance.tkuser.save()

# @receiver(post_save, sender=User)
# def save_tkuser(sender, instance, **kwargs):
#     try:
#         instance.tkuser.save()
#     except Exception as e:
#         print(Exception)
#         TkUser.objects.create(user=instance, adzone=None)


class Adzone(models.Model):
    pid = models.CharField(max_length=64, db_index=True, unique=True)
    adzone_name = models.CharField(max_length=32, db_index=True)
    # 30天点击数
    click_30d = models.IntegerField(default=0)
    # 30天付款笔数
    alipay_num_30d = models.IntegerField(default=0)
    # 30天预估收入
    rec_30d = models.FloatField(default=0)
    # 30天效果预估
    alipay_rec_30d = models.FloatField(default=0)

    last_update = models.DateTimeField()
    create_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.create_time = timezone.now()
        self.last_update = timezone.now()
        super(Adzone, self).save(*args, **kwargs)

from django.utils import timezone
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


@receiver(post_save, sender=User)
def create_pushtime(sender, instance, created, **kwargs):
    if created:
        PushTime.objects.create(user=instance)