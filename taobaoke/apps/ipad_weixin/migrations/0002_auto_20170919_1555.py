# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-19 07:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipad_weixin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qrcode',
            name='head_img_url',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='qrcode',
            name='password',
            field=models.TextField(),
        ),
    ]
