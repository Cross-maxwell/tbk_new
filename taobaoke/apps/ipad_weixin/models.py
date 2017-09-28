# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import datetime

import logging
logger = logging.getLogger('django_models')


class Img(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=250, unique=True)
    type = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name


class Contact(models.Model):

    msg_type = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    nickname = models.CharField(max_length=200)
    signature = models.CharField(max_length=200)
    small_head_img_url = models.URLField(max_length=200)
    big_head_img_url = models.URLField(max_length=200)
    province = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    remark = models.CharField(max_length=200)
    alias = models.CharField(max_length=200)
    sex = models.CharField(max_length=200)
    contact_type = models.CharField(max_length=200)
    chat_room_owner = models.CharField(max_length=200)
    ext_info = models.TextField(default='', null=True)
    ticket = models.CharField(max_length=200)
    chat_room_version = models.CharField(max_length=200)

    last_update = models.DateTimeField(null=True)
    create_at = models.DateTimeField(null=True)
    remove_at = models.DateTimeField(null=True)  # Record removed time. Default None.

    """
    在models中的方法应该是什么样子的？
    """

    def update_from_mydict(self, msg_dict):
        self.msg_type = msg_dict['MsgType']
        self.nickname = msg_dict['NickName']
        self.signature = msg_dict['Signature']
        self.small_head_img_url = msg_dict['SmallHeadImgUrl']
        self.big_head_img_url = msg_dict['BigHeadImgUrl']
        self.province = msg_dict['Province']
        self.city = msg_dict['City']
        self.remark = msg_dict['Remark']
        self.alias = msg_dict['Alias']
        self.sex = msg_dict['Sex']
        self.contact_type = msg_dict['ContactType']
        self.chat_room_owner = msg_dict['ChatRoomOwner']
        self.ext_info = msg_dict['ExtInfo']
        self.ticket = msg_dict['Ticket']
        self.chat_room_version = msg_dict['ChatroomVersion']


    def save(self, *args, **kwargs):
        """
        重载save()方法来记录每次更新的时间，以及创建时间
        :param args:
        :param kwargs:
        :return:
        """
        if not self.create_at:
            self.create_at = datetime.datetime.now()
        self.last_update = datetime.datetime.now()
        return super(Contact, self).save(*args, **kwargs)


class Qrcode(models.Model):
    check_time = models.CharField(max_length=200)
    expired_time = models.CharField(max_length=200)
    head_img_url = models.TextField()
    nickname = models.CharField(max_length=200)
    notify_key = models.CharField(max_length=200)
    password = models.TextField()
    random_key = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    uuid = models.CharField(max_length=200)
    md_username = models.CharField(max_length=200)

    @classmethod
    def save_qr_code(cls, qr_code):
        try:
            qrcode_db = cls(
                check_time=qr_code['CheckTime'], expired_time=qr_code['ExpiredTime'],
                head_img_url=qr_code['HeadImgUrl'], nickname=qr_code['Nickname'],
                notify_key=qr_code['NotifyKey'], password=qr_code['Password'],
                random_key=qr_code['RandomKey'], status=qr_code['Status'],
                username=qr_code['Username'], uuid=qr_code['Uuid'], md_username=''
            )
            qrcode_db.save()
        except Exception as e:
            logger.error(e)
            print("---save_qr_code error---")

    def update_from_qrcode(self, qrcode):
        self.check_time = qrcode['CheckTime']
        self.expired_time = qrcode['ExpiredTime']
        self.head_img_url = qrcode['HeadImgUrl']
        self.nickname = qrcode['Nickname']
        self.password = qrcode['Password']
        self.random_key = qrcode['RandomKey']
        self.status = qrcode['Status']
        self.username = qrcode['Username']

        if self.uuid is not None or self.uuid != '':
            pass
        else:
            self.uuid = qrcode['Uuid']


class BotParam(models.Model):
    username = models.CharField(max_length=200, unique=True)
    device_id = models.CharField(max_length=200)
    long_host = models.CharField(max_length=200)
    short_host = models.CharField(max_length=200)

    @classmethod
    def save_bot_param(cls, username, device_id, long_host, short_host):
        try:
            bot_param_db = cls(username=username, device_id=device_id, long_host=long_host, short_host=short_host)
            bot_param_db.save()
        except Exception as e:
            logger.error(e)
            print('---save bot_param failed---')

    @classmethod
    def update_bot_param(cls, bot_param_db, username, device_id, long_host, short_host):
        try:
            bot_param_db.username = username
            bot_param_db.device_id = device_id
            bot_param_db.long_host = long_host
            bot_param_db.short_host = short_host
            bot_param_db.save()
        except Exception as e:
            logger.error(e)
            print('---update qrcode failed---')


class WxUser(models.Model):
    auto_auth_key = models.CharField(max_length=200)
    cookies = models.CharField(max_length=200)
    current_sync_key = models.CharField(max_length=250)
    device_id = models.CharField(max_length=200)
    device_name = models.CharField(max_length=200)
    device_type = models.CharField(max_length=200)
    max_sync_key = models.CharField(max_length=200)
    nickname = models.CharField(max_length=200)
    session_key = models.CharField(max_length=200)
    uin = models.CharField(max_length=200, unique=True)
    user_ext = models.CharField(max_length=250)
    username = models.CharField(max_length=250)
    login = models.IntegerField(default=0)

    last_update = models.DateTimeField(null=True)
    create_at = models.DateTimeField(null=True)

    def update_wxuser_from_userobject(self, v_user):
        self.auto_auth_key = ''
        self.cookies = ''
        self.device_id = v_user.deviceId
        self.nickname = v_user.nickname
        self.session_key = v_user.sessionKey
        self.username = v_user.userame
        self.login = 1

    def save(self, *args, **kwargs):
        """
        重载save()方法来记录每次更新的时间，以及创建时间
        """
        if not self.create_at:
            self.create_at = datetime.datetime.now()
        self.last_update = datetime.datetime.now()
        return super(WxUser, self).save(*args, **kwargs)


class Message(models.Model):
    content = models.TextField()
    create_time = models.CharField(max_length=200)
    from_username = models.CharField(max_length=200)
    img_buf = models.CharField(max_length=200)
    img_status = models.CharField(max_length=200)
    msg_id = models.CharField(max_length=200, unique=True)
    msg_source = models.CharField(max_length=200)
    msg_type = models.CharField(max_length=200)
    new_msg_id = models.CharField(max_length=200)
    push_content = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    to_username = models.CharField(max_length=200)

    def update_from_msg_dict(self, msg_dict):
        self.content = msg_dict['Content']
        self.create_time = msg_dict['CreateTime']
        self.from_username = msg_dict['FromUserName']
        self.img_buf = ''
        self.img_status = msg_dict['ImgStatus']
        self.msg_source = msg_dict['MsgSource']
        self.msg_type = msg_dict['MsgType']
        self.new_msg_id = msg_dict['NewMsgId']
        self.push_content = msg_dict['PushContent']
        self.status = msg_dict['Status']
        self.to_username = msg_dict['ToUserName']


class SignInRule(models.Model):
    group_name = models.CharField(max_length=200)
    keyword = models.TextField()
    red_packet_id = models.CharField(max_length=100)


