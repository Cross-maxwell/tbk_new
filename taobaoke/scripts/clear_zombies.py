# coding: utf-8
"""
用于清理3个月没登录的用户, 将其pid移除
"""

import sys
sys.path.append('/home/new_taobaoke/taobaoke')

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone

# Users that had never logged in.
never_logined_users = User.objects.filter(last_login__isnull=True)
# Users that had never logged in since data migration in 2017.10.27.
acient_users = User.objects.filter(last_login__lte=datetime(2017,10,27,0,0,0))
# Users that had never logged in in last three months.
forgotten_users = User.objects.filter(last_login__lte=timezone.now()-timedelta(weeks=12))

for u in never_logined_users:
    u.tkuser.adzone = None
    u.tkuser.save()

for u in acient_users:
    u.tkuser.adzone = None
    u.tkuser.save()

for u in forgotten_users:
    u.tkuser.adzone = None
    u.tkuser.save()