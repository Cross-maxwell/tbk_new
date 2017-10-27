# _*_ coding:utf-8 _*_
'''
10/27 12:33检查无误
'''


import os
import sys
import django

sys.path.append("/Users/hong/sourcecode/work/BotService")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fuli.settings")
django.setup()

from broadcast.models.user_models import TkUser
from account.models.commision_models import Commision, AgentCommision
'''
脚本功能：
    结算转帐之前对佣金进行一次总计算，以便在帐户中转入充足的金额
    可计算指定用户的佣金情况
'''


def get_all_commission(mode="weekly", user_id=None):
    """
    计算用户佣金
    """
    if mode not in ['weekly', 'monthly', 'all']:
        print "cal all commission with error mode"
        return None

    try:
        if user_id is None:
            commision_list = Commision.objects.all()
        else:
            mode = 'all'
            commision_list = Commision.objects.filter(user_id=str(user_id))
        sum = 0

        for commision in commision_list:
            if user_id is not None:
                # 函数传参指定 user_id 时,userlist中只有一个filter出来的用户，计算即可
                sum += commision.balance
            else:
                # 传参不指定user_id时，分周结和月结:
                weekly_condition = mode == 'weekly' and int(commision.user_id) < 700
                monthly_condition = mode == 'monthly' and int(commision.user_id) >= 700
                all = mode == 'all'
                if weekly_condition or monthly_condition or all:
                    sum += commision.balance
        return sum
    except Exception as e:
        print "cal commission exception:{0}".format(e.message)


def get_all_agent_commission(mode="weekly", user_id=None):
    """
    计算下级代理总佣金
    """
    if mode not in ['weekly', 'monthly', 'all']:
        print "cal all commission with error mode"
        return None

    try:
        # 取在下级代理佣金表所有用户
        agent_commision_list = AgentCommision.objects.filter(balance__gt=0)
        sum = 0

        for agc in agent_commision_list:
            # 拿到该下级代理的上级user_id
            inviter_id = TkUser.objects.get(user_id=int(ag.user_id)).inviter_id

            if user_id is not None:
                # 函数传参指定user_id时二级佣金计算
                if int(inviter_id) == int(user_id):
                    print agc.user_id
                    sum += agc.balance
            else:
                # 传参不指定user_id时，分周结和月结:
                weekly_condition = mode == 'weekly' and int(agc.user_id) < 700
                monthly_condition = mode == 'monthly' and int(agc.user_id) >= 700
                all = mode == 'all'
                if weekly_condition or monthly_condition or all:
                    sum += agc.balance
        return sum
    except Exception as e:
        print "cal agent commission exception:{0}".format(e.message)


if __name__ == "__main__":
    """
    mode:
        weekly:周结用户 id < 700
        monthly:月结用户 id >= 700
        all:所有用户
    """
    # 不指定计算某用户时，设为None
    user_id = None
    mode = 'weekly'

    s1 = get_all_commission(mode, user_id=user_id)
    s1 = s1 if s1 is not None else 0

    s2 = get_all_agent_commission(mode, user_id=user_id)
    s2 = s2 if s2 is not None else 0

    print "**************************"
    print "一级代理佣金:{0}".format(s1)
    print "二级代理佣金:{0}".format(s2)
    print "总共:{}".format(s1 + s2)
    print "**************************"
