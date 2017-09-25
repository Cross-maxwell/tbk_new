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


class TkUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    #username,password

    adzone = models.ForeignKey('Adzone', db_column='adzone_key', null=True)
    search_url_template = models.CharField(max_length=128, null=True)

    def get_adzone_id(self):
        return self.adzone.pid.split('_')[-1]

    def get_search_url(self, keyword):
        """http://dianjin532.123nlw.com/saber/index/search?pid=mm_122190119_26062749_103176155&search={keyword}"""
        return unicode(self.search_url_template).format(keyword=keyword)

    def assign_pid(self):
        try:
            available_adzone = Adzone.objects.filter(tkuser=None)[0]
            self.adzone = available_adzone
        except Exception as exc:
            requests.post(
                'https://hook.bearychat.com/=bw8NI/incoming/ab2346561ad4c593ea5b9a439ceddcfc',
                json={'text': '分配PID出现异常.' + exc.message}
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
            user = User.objects.create_user(username=username)
            return TkUser.objects.get(user=user)



"""
定义一个全局的Signal，属于扩展User字段的行为，那么当我的sender为User，且有一个post_save[即数据库的保存]行为时，
我们去创建自己的附属User,TkUser
instance是User的一个实例
"""

@receiver(post_save, sender=User)
def create_tkuser(sender, instance, created, **kwargs):
    if created:
        TkUser.objects.create(user=instance, adzone=None)


@receiver(post_save, sender=User)
def save_tkuser(sender, instance, **kwargs):
    instance.tkuser.save()



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

