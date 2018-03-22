#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/03/2018 11:30
# @Author  : Jaelyn
# @Site    : 
# @File    : new_tbk_alipay_send_run.py
# @Software: PyCharm

# coding:utf-8

###############
# 进行转账动作. #
###############

from __future__ import print_function
import json
import os
from datetime import datetime
import django
import sys
import requests
from django.db import transaction

reload(sys)
sys.setdefaultencoding('utf8')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fuli.settings")
django.setup()
from account.models.commision_models import Commision, AgentCommision, AlipayAccount
from account.utils.transfer_utils import pay
from account.utils.commision_utils import cut_decimal
from fuli.oss_utils import beary_chat
# from common_utils import beary_chat, cut_decimal
from account.utils.commision_utils import withdraw_commision, withdraw_agent_commision
from broadcast.models.user_models import TkUser

admin_name_in_beary_chat = "fatphone777"


def log(log_text):
    file_name = "transfer_log_{0}.txt".format(datetime.now().strftime('%Y-%m-%d'))
    print(log_text)
    with open(file_name, 'a') as f:
        if type(log_text) == str:
            f.write(log_text)
        elif type(log_text) == dict:
            f.write(log_text.get('text'))
        f.write('\r\n')


'''
 : process 本方法向tbk_alipay_transfer_url发送请求，即实际转账动作。
 : reference tbk_alipay_transfer_url 果粉街域名下的支付宝转账接口
 : return 成功返回True，
                   失败返回False。
'''


def remote_transfer(alipay_account, alipay_name, amount):
    amount = cut_decimal(amount)
    try:
        result = pay(
            account=alipay_account,
            name=alipay_name,
            amount=amount
        )
        if result['code'] == '10000':
            log("Successful Transfering {0} Yuan to {1} - {2}.".format(amount, alipay_account, alipay_name))
            return True
        else:
            log(
                "Transfer Failed: {0} - {1} Because of {2}  With out_biz_no As {3} code {4} sub_code {5} sub_msg {6}".format(
                    alipay_account, alipay_name, result['msg'], result['out_biz_no'], result['code'],
                    result['sub_code'], result['sub_msg']))
            return False
    except Exception as e:
        log("Exception ocourred:{0} When Paying {1} Yuan To {2}".format(e, amount, alipay_account))
        return False


# 根据user_id，从TkUser表中获取被其推荐的二级代理列表，
# 并获取此些用户的balance总额
def get_sub_agent_contribution(user_id):
    sub_agent_list = TkUser.objects.filter(inviter_id=user_id)
    amount = 0
    for sub_agent in sub_agent_list:
        try:
            # Generally, this object already created when calculate commision contributed by sub-agent
            sub_agent_commision = AgentCommision.objects.get(user_id=sub_agent.user_id)
            # 舍弃分之后的数,留着累计
            amount += cut_decimal(sub_agent_commision.balance, 2)
        except Exception as e:
            log("get_sub_agent_contribution error:" + e.message + " sub_agent_id:" + str(sub_agent.user_id))
    return amount


# 转账行为：
def transfer(user_id=None):
    # 若未传入 user_id，则针对所有用户结帐。
    if user_id is None:
        commision = Commision.objects.all()
    else:
        commision = Commision.objects.filter(user_id=user_id)

    for commision in commision:
        # 当前用户id
        c_user_id = commision.user_id
        log('-----------------------')
        log('transfer start user_id:' + str(c_user_id))
        # 若没有绑定支付宝帐号则跳过该用户
        try:
            alipay_account = AlipayAccount.objects.get(user_id=c_user_id)
        except Exception as e:
            log("User_id:{0} Never Bind Alipay Account.".format(c_user_id))
            continue
        alipay_id = alipay_account.alipay_id
        alipay_name = alipay_account.alipay_name
        balance = commision.balance
        if commision.balance > 0:

            # 重要改动：确定数据库操作无误后再执行转账动作，将withdraw_commision作为remote_transfer的前置
            if not withdraw_commision(c_user_id, balance):
                msg = "User_id:{0}  Balance:{1}  Withdraw Error".format(c_user_id, balance)
                beary_chat(msg, user=admin_name_in_beary_chat)
                continue
            else:
                log("Remote Transfer Commision:{0}".format(balance))
                if not remote_transfer(alipay_id, alipay_name, balance):
                    msg = "User_id:{0}  Aplipay_id:{1}  Commision_balance:{2}".format(c_user_id, alipay_id, balance)
                    beary_chat(msg, user=admin_name_in_beary_chat)
                    log("Commision Remote Transfer Error:" + msg)
                    continue
                else:
                    log("Update Commision Success.")

            # if not remote_transfer(alipay_id, alipay_name, balance):
            #     msg = "User_id:{0}  Aplipay_id:{1}  Commision_balance:{2}".format(c_user_id, alipay_id, balance)
            #     beary_chat(msg, user=admin_name_in_beary_chat)
            #     log("Commision Remote Transfer Error:"+msg)
            #     continue
            # else:
            #     log("Transfer Commision:{0}".format(balance))
            #     if not withdraw_commision(c_user_id, balance):
            #         msg = "User_id:{0}  Balance:{1}  Withdraw Error".format(c_user_id, balance)
            #         beary_chat(msg, user=admin_name_in_beary_chat)
            #         continue
            #     else:
            #         log("Update Commision Success.")
        else:
            log('No Commision to Pay.')

        # 二级代理佣金
        subagent_commision = get_sub_agent_contribution(commision.user_id)
        if subagent_commision > 0:
            if not remote_transfer(alipay_id, alipay_name, subagent_commision):
                msg = "User_id:{0}  Aplipay_id:{1}  subagent_commision:{2}".format(c_user_id, alipay_id,
                                                                                   subagent_commision)
                beary_chat(msg, user=admin_name_in_beary_chat)
                log("Subagent_commision Remote Transfer Error:" + msg)
                continue
            else:
                withdraw_agent_commision(commision.user_id)
                log("Remote Transfer Subagent_commision:{0}".format(subagent_commision))
                log("update AgentCommision success")

        else:
            log('No Subagent Commision to Pay.')
        log("User_id:{0}  Tranfer  Finish".format(commision.user_id))




if __name__ == "__main__":
    transfer(user_id=2243)
    pass
