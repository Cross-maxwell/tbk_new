# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-08 07:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200, unique=True)),
                ('device_id', models.CharField(max_length=200)),
                ('long_host', models.CharField(max_length=200)),
                ('short_host', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('nickname', models.CharField(max_length=100)),
                ('signature', models.CharField(max_length=200)),
                ('small_head_img_url', models.URLField()),
                ('big_head_img_url', models.URLField()),
                ('province', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('alias', models.CharField(max_length=100)),
                ('chat_room_owner', models.CharField(max_length=200)),
                ('chat_room_version', models.CharField(default='', max_length=50)),
                ('member_nums', models.IntegerField(default=0)),
                ('is_send', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ChatroomMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('nickname', models.CharField(default='', max_length=200)),
                ('small_head_img_url', models.URLField(default='')),
                ('inviter_username', models.CharField(default='', max_length=100)),
                ('created', models.DateTimeField(auto_now=True)),
                ('is_delete', models.BooleanField(default=False)),
                ('chatroom', models.ManyToManyField(db_index=True, to='ipad_weixin.ChatRoom')),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('msg_type', models.CharField(max_length=200)),
                ('username', models.CharField(max_length=200, unique=True)),
                ('nickname', models.CharField(max_length=200)),
                ('signature', models.CharField(max_length=200)),
                ('small_head_img_url', models.URLField()),
                ('big_head_img_url', models.URLField()),
                ('province', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('remark', models.CharField(max_length=200)),
                ('alias', models.CharField(max_length=200)),
                ('sex', models.CharField(max_length=200)),
                ('contact_type', models.CharField(max_length=200)),
                ('chat_room_owner', models.CharField(max_length=200)),
                ('ext_info', models.TextField(default='', null=True)),
                ('ticket', models.CharField(max_length=200)),
                ('chat_room_version', models.CharField(max_length=200)),
                ('last_update', models.DateTimeField(null=True)),
                ('create_at', models.DateTimeField(null=True)),
                ('remove_at', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Img',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField(max_length=250, unique=True)),
                ('type', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('create_time', models.CharField(max_length=200)),
                ('from_username', models.CharField(max_length=200)),
                ('img_buf', models.CharField(max_length=200)),
                ('img_status', models.CharField(max_length=200)),
                ('msg_id', models.CharField(max_length=200, unique=True)),
                ('msg_source', models.CharField(max_length=200)),
                ('msg_type', models.CharField(max_length=200)),
                ('new_msg_id', models.CharField(max_length=200)),
                ('push_content', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('to_username', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Qrcode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_time', models.CharField(max_length=200)),
                ('expired_time', models.CharField(max_length=200)),
                ('head_img_url', models.TextField()),
                ('nickname', models.CharField(max_length=200)),
                ('notify_key', models.CharField(max_length=200)),
                ('password', models.TextField()),
                ('random_key', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('username', models.CharField(max_length=200)),
                ('uuid', models.CharField(max_length=200)),
                ('md_username', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='SignInRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=200)),
                ('keyword', models.TextField()),
                ('red_packet_id', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='WxUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_auth_key', models.CharField(max_length=200)),
                ('cookies', models.CharField(max_length=200)),
                ('current_sync_key', models.CharField(max_length=250)),
                ('device_id', models.CharField(max_length=200)),
                ('device_name', models.CharField(max_length=200)),
                ('device_type', models.CharField(max_length=200)),
                ('max_sync_key', models.CharField(max_length=200)),
                ('nickname', models.CharField(max_length=200)),
                ('session_key', models.CharField(max_length=200)),
                ('uin', models.CharField(max_length=200, unique=True)),
                ('user_ext', models.CharField(max_length=250)),
                ('username', models.CharField(max_length=250)),
                ('login', models.IntegerField(default=0)),
                ('last_update', models.DateTimeField(null=True)),
                ('create_at', models.DateTimeField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='contact',
            name='wx_user',
            field=models.ManyToManyField(to='ipad_weixin.WxUser'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='wx_user',
            field=models.ManyToManyField(to='ipad_weixin.WxUser'),
        ),
    ]
