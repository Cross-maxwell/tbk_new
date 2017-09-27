# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()


def filter_sign_in_keyword(wx_id, msg_dict):
    keyword = msg_dict['Content']
    # keyword_db数据库中取出群所对应的红包id