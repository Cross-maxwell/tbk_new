# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-22 04:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipad_weixin', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatroom',
            options={'verbose_name': 'chatroom'},
        ),
        migrations.AddField(
            model_name='wxuser',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wxuser',
            name='uuid',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='signinrule',
            name='keyword',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='wxuser',
            name='last_heart_beat',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
