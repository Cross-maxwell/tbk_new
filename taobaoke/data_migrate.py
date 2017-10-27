# -*- coding: utf-8 -*-

import requests
import re
import sys
# sys.path.append('/home/new_taobaoke/taobaoke/')
import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from django.contrib.auth.models import User

import json
with open('/home/smartkeyerror/PycharmProjects/BotService/data.json', 'r') as f:
    json_data = f.read()

data_list = json.loads(json_data)

user_list = User.objects.all()
username_list = [user.username for user in user_list]

for data in data_list:
    # 15900000000, xxxxx
    for ipad_user in user_list:
        username = ipad_user.username
        password = ipad_user.password
        if data['username'] == username:
            ipad_user.password = data['password']
            ipad_user.save()
            print(ipad_user.username)
            break

    if data['username'] in username_list:
        continue
    try:
        User.objects.create_user(username=data['username'], password=data['password'])
    except Exception as e:
        print("Duplicate")

"""
原 13632909405
pbkdf2_sha256$36000$Yp3hO6P9oW0H$navlR5LxR69GFbDyv72mDzXDcDWWHbxMvEsUeqm1wW0=

Bot 13632909405
pbkdf2_sha256$24000$ePizyffaLida$2BVw2t2aqHhCLYCPIXo6Oi4ZdeGxFRpii2kyEKt1JbI=
"""