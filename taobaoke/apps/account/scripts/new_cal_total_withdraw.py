#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/03/2018 11:29
# @Author  : Jaelyn
# @Site    : 
# @File    : new_cal_total_withdraw.py
# @Software: PyCharm

# _*_ coding:utf-8 _*_
'''
脚本功能：
    结算转帐之前对佣金进行一次总计算，以便在帐户中转入充足的金额
    可计算指定用户的佣金情况

变更：
    2018.01.31：目前已不存在周结和月结之分
'''

import os
import sys
import django


sys.path.append("/home/adam/mydev/projects/new_sys/taobaoke") # todo 路径修改
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TianTian.settings")
django.setup()

from broadcast.models.user_models import TkUser
from account.models.commision_models import Commision, AgentCommision


def get_commission(user_id=None):
    """
    计算所有佣金， 可指定user_id，不指定则为全部
    """
    try:
        if user_id is None:
            commision_list = Commision.objects.all()
        else:
            commision_list = Commision.objects.filter(user_id=str(user_id))

        sum = 0
        for commision in commision_list:
            sum += commision.balance
        return sum
    except Exception as e:
        print "cal commission exception:{0}".format(e.message)


def get_agent_commission(user_id=None):
    """
    计算下级代理总佣金，可指定user_id，不指定则为全部
    """
    try:
        # 取在下级代理佣金表所有用户
        if user_id is None:
            agent_commision_list = AgentCommision.objects.filter(balance__gt=0)
        else:
            agent_commision_list = AgentCommision.objects.filter(user__tkuser__inviter_id=user_id, balance__gt=0)

        sum = 0
        for agc in agent_commision_list:
            sum += agc.balance
        return sum
    except Exception as e:
        print "cal agent commission exception:{0}".format(e.message)


# def get_third_commission


if __name__ == "__main__":
    # 不指定计算某用户时，设为None

    user_id = 2243

    s1 = get_commission(user_id)
    s1 = s1 if s1 is not None else 0
    s2 = get_agent_commission(user_id)
    s2 = s2 if s2 is not None else 0

    print "**************************"
    print "一级代理佣金:{0}".format(s1)
    print "二级代理佣金:{0}".format(s2)
    print "总共:{}".format(s1 + s2)
    print "**************************"
