# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-11 06:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Adzone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.CharField(db_index=True, max_length=64, unique=True)),
                ('adzone_name', models.CharField(db_index=True, max_length=32)),
                ('click_30d', models.IntegerField(default=0)),
                ('alipay_num_30d', models.IntegerField(default=0)),
                ('rec_30d', models.FloatField(default=0)),
                ('alipay_rec_30d', models.FloatField(default=0)),
                ('last_update', models.DateTimeField()),
                ('create_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=None)),
                ('last_update', models.DateTimeField(default=None)),
                ('available', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PushRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('group', models.CharField(max_length=64)),
                ('data_string', models.TextField(default='', max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='TkUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_url_template', models.CharField(max_length=128, null=True)),
                ('adzone', models.ForeignKey(db_column='adzone_key', null=True, on_delete=django.db.models.deletion.CASCADE, to='broadcast.Adzone')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='broadcast.Entry')),
                ('title', models.CharField(db_index=True, max_length=256)),
                ('desc', models.TextField(max_length=200)),
                ('img_url', models.TextField(max_length=512)),
                ('cupon_value', models.FloatField()),
                ('price', models.FloatField()),
                ('sold_qty', models.IntegerField()),
                ('cupon_left', models.IntegerField()),
                ('tao_pwd', models.CharField(max_length=32, null=True)),
                ('cupon_url', models.TextField(max_length=1024)),
                ('cupon_short_url', models.URLField(db_index=True, null=True)),
                ('recommend', models.CharField(max_length=128, null=True)),
                ('item_id', models.CharField(db_index=True, max_length=64, unique=True)),
            ],
            bases=('broadcast.entry',),
        ),
        migrations.AddField(
            model_name='pushrecord',
            name='entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='broadcast.Entry'),
        ),
    ]
