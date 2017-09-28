# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()


def filter_sign_in_keyword(wx_id, msg_dict):
    # wx_id 群主id
    keyword = msg_dict['Content']
    # keyword_db数据库中取出群所对应的红包id
    """
    wx_id中包括谁在哪儿说了什么，以及说话的时间
    该数据库应有字段：
        群名称-关键词-红包id
    """