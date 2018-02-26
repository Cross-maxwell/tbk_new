# coding:utf-8

'''
进行转账动作.
'''

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
# sys.path.append("/Users/hong/sourcecode/work/BotService")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fuli.settings")
django.setup()
from account.models.commision_models import Commision, AgentCommision, AlipayAccount
from account.utils.transfer_utils import pay
from account.utils.common_utils import cut_decimal
from account.utils.commision_utils import withdraw_commision, withdraw_agent_commision
from broadcast.models.user_models import TkUser

admin_name_in_beary_chat = "fatphone777"


def log(log_text):
    file_name = "transfer_log_{0}.txt".format(datetime.now().strftime('%Y-%m-%d'))
    print(log_text)
    with open(file_name, 'a') as f:
        if type(log_text)==str:
            f.write(log_text)
        elif type(log_text)==dict:
            f.write(log_text.get('text'))
        f.write('\r\n')


def beary_chat(text, url=None, user=None, channel=None):
    requests.post(
        'https://hook.bearychat.com/=bw8NI/incoming/ab2346561ad4c593ea5b9a439ceddcfc',
        json={
            'text': text,
            "channel": channel,
            "user": user,
            "attachments": [
                {
                    "images": [{"url": url}]
                }
            ]
        }
    )


def remote_transfer(alipay_account, alipay_name, amount):
    '''
     : process 本方法使用支付宝SDK，发起转账。
     : return 成功返回True，
                       失败返回False。
    '''
    amount = cut_decimal(amount, 2)
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
            log("Transfer Failed: {0} - {1} Because of {2}  With out_biz_no As {3} ".format(alipay_account, alipay_name, result['msg'], result['out_biz_no']))
            return False
    except Exception as e:
        log("Exception ocourred:{0} When Paying {1} Yuan To {2}".format(e.message, amount, alipay_account))
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
    dt_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log("Transfer Start at {}".format(dt_start))
    # 若未传入 user_id，则针对所有用户结帐。
    if user_id is None:
        commisions = Commision.objects.all()
    else:
        commisions = Commision.objects.filter(user_id=user_id)

    for commision in commisions:
        # get alipay account info
        log('-----------------------')
        log('transfer start user_id:' + str(commision.user_id))
        try:
            alipay_account = AlipayAccount.objects.get(user_id=commision.user_id)
        except AlipayAccount.DoesNotExist:
            log("user_id:{0} alipay_account doesn't exist".format(commision.user_id))
            continue

        if commision.balance > 0:
            # access remote alipay-transfer api
            # transfer commision
            if not remote_transfer(
                    alipay_account.alipay_id,
                    alipay_account.alipay_name,
                    commision.balance):
                msg = "user_id:{0} aplipay_id:{1} commision_balance:{2}".format(
                    commision.user_id,
                    alipay_account.alipay_id,
                    commision.balance
                )
                beary_chat(msg, user=admin_name_in_beary_chat)
                log("commision remote transfer error:"+msg)
                continue
            else:
                log("transfer commision:{0}".format(commision.balance))

                # update database
                if not withdraw_commision(commision.user_id, commision.balance):
                    msg = "user_id:{0} balance:{1} withdraw error".format(commision.user_id, commision.balance)
                    beary_chat(msg, user=admin_name_in_beary_chat)
                    continue
                else:
                    log("update commision success")

        # transfer sub-agent commision
        commision_from_subagent = get_sub_agent_contribution(commision.user_id)
        if commision_from_subagent > 0:
            if not remote_transfer(
                    alipay_account.alipay_id,
                    alipay_account.alipay_name,
                    commision_from_subagent):
                msg = "user_id:{0} aplipay_id:{1} commision_from_subagent:{2}".format(
                    commision.user_id,
                    alipay_account.alipay_id,
                    commision_from_subagent
                )
                beary_chat(msg, user=admin_name_in_beary_chat)
                log("commision_from_subagent remote transfer error:" + msg)
                continue
            else:
                log("transfer commision_from_subagent:{0}".format(commision_from_subagent))
                # update database
                withdraw_agent_commision(commision.user_id)
                log("update AgentCommision success")
        log("user_id:{0} tranfer finish".format(commision.user_id))

    dt_done = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log("Done at {}".format(dt_done))

if __name__ == "__main__":
    transfer(user_id=None)



