# coding=utf-8
from account.models.commision_models import Account, AccountFlow
from django.db import transaction
import traceback

'''
维护账户表Account及流水AccountFlow
'''

def post(user_id, amount, in_or_out, order_id, type):
    """
    :param md_user_id: 用户id
    :param amount: 金额
    :param in_or_out: True or False
    :param order_id: 订单id
    :param type: 代理 淘宝客 诸如此类
    :return: True or False
    """
    try:
        # 拿到账户
        try:
            account = Account.objects.get(user_id=user_id)
        except Account.DoesNotExist:
            account = Account.objects.create(user_id=user_id)

        account_flow = AccountFlow.objects.create(user_id=user_id)

        in_or_out_flag = 1 if in_or_out else -1

        with transaction.atomic():
            # 写入基础信息
            account_flow.in_or_out = in_or_out
            account_flow.order_id = order_id
            account_flow.amount = amount
            account_flow.type = type
            account_flow.save()

            # 扣钱or进钱
            account.amount += amount * in_or_out_flag
            account.save()
        return True
    except Exception, e:
        traceback.print_exc()
        return False
