# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-18 04:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipad_weixin', '0003_auto_20171017_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wxuser',
            name='uuid',
            field=models.CharField(default='', max_length=150),
        ),
    ]