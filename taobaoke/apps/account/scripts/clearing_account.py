# coding:utf-8

'''
维护Account和AccountFlow
'''

import os
import django
import sys
from __future__ import absolute_import


sys.path.append("/Users/hong/sourcecode/work/BotService")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BotService.settings")
django.setup()

if __name__ == '__main__':
    """
    这个脚本会每天在凌晨执行代理清算逻辑
    
    """
    # 测试账号转存
    from account.utils import account_utils
    account_utils.post(1, 1, False, 1, 'test')
    isinstance('1', basestring)
