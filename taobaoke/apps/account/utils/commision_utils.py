# coding:utf-8


from django.db import transaction
from account.utils import user_utils, order_utils, account_utils
from account.models.commision_models import Commision, AgentCommision
from account.models.order_models import AgentOrderStatus
from django.contrib.auth.models import User
from broadcast.models.user_models import TkUser
from common_utils import cut_decimal


'''
以下三个方法为链式调用, 用以维护agent_commision数据
直接使用calc_agent_commision即可.
'''
def cal_agent_commision():
    # 拿到所有下线
    user_list = User.objects.filter(is_staff=False, last_login__isnull=False)
    for user in user_list:
        sub_agent_list = user_utils.get_next_level_user(user.username)
        print("{}共有{}名下级淘宝客代理".format(user.username, len(sub_agent_list)))

        for sub_agent in sub_agent_list:

            # 通过下线的user，去拿到所有结算订单
            order_list = order_utils.get_order_list_by_user(sub_agent, u'订单结算', True)
            print("代理{}已经成了{}单".format(sub_agent.username, len(order_list)))

            # 拿到代理的账户
            agent_commision = get_agent_commision_account(sub_agent)

            # 开始遍历这个代理的所有订单
            for order in order_list:
                with transaction.atomic():
                    # 如果这笔订单的状态是True，说明不需要再入账
                    if not get_or_update_AgentOrderStatus(order.id):

                        # 计算这笔佣金
                        order_commision_rate  = round(float(order.commision_amount)/order.pay_amount,2)
                        if order.pay_amount >500 and order_commision_rate <0.25:
                            order_commision = order.pay_amount * order_commision_rate*0.1
                        else:
                            order_commision = order.pay_amount * agent_commision.commision_rate

                        # 入账到agent_commision中
                        agent_commision.sum_earning_amount += order_commision
                        agent_commision.balance += order_commision
                        agent_commision.save()

def get_or_update_AgentOrderStatus(order_id):
    """
    创建一级代理订单状态
    如果这笔订单，已经入过账，不会再创建
    :param order_id:
    :return:
    """
    try:
        AgentOrderStatus.objects.get(order_id=order_id, enter_account=True)
        return True
    except AgentOrderStatus.DoesNotExist:
        AgentOrderStatus.objects.create(order_id=order_id, enter_account=True)
        return False

def get_agent_commision_account(user):
    """
    安全拿到代理佣金账户，如果没有，则创建
    :param user:
    :return:
    """
    try:
        agent_commision = AgentCommision.objects.get(user_id=str(user.id))
    except AgentCommision.DoesNotExist:
        agent_commision = AgentCommision.objects.create(user_id=str(user.id))
    return agent_commision


'''
用以维护commision数据
'''
def cal_commision():
    """
    计算订单佣金增量
    :return:
    """
    user_list = User.objects.filter(is_staff=False, last_login__isnull=False)
    from account.models.commision_models import Commision
    from account.models.order_models import Order
    for user in user_list:
        user_id = str(user.id)
        try:
            commision = Commision.objects.get(user_id=user_id)
        except Commision.DoesNotExist:
            commision = Commision.objects.create(user_id=user_id)
        ad_id = order_utils.get_ad_id(user.username)
        if ad_id is None:
            continue
        order_list = Order.objects.filter(ad_id=ad_id, order_status=u'订单结算', enter_account=False)
        new_earning_amount = 0

        with transaction.atomic():
            for order in order_list:
                pay_amount = order.pay_amount
                order_commision_rate = round(float(order.commision_amount)/order.pay_amount,2)
                if pay_amount >500 and order_commision_rate<0.25:
                    order_commision = pay_amount * order_commision_rate*0.5
                else:
                    order_commision = order.show_commision_amount
                new_earning_amount += order_commision
                order.enter_account = True
                order.save()
                account_utils.post(user_id, order_commision, True, order.order_id, 'order_commision')

            commision.sum_earning_amount += new_earning_amount
            commision.balance += new_earning_amount
            commision.save()



"""
判断是否可提现,
参数withdraw_amount是申请提现金额
"""
def withdraw_commision(user_id, withdraw_amount):
    """
    淘宝客提现操作
    :param md_user_id:用户id(string)
    :param withdraw_amount: 提现总额(float)
    :return: 提现操作结果 True-成功 False-失败
    """
    try:
        commision = Commision.objects.get(user_id=user_id)
        if withdraw_amount > commision.balance:
            print "withdraw error:withdraw_amount is greater than balance->" \
                  "amount:{0},balance:{1},id:{2}".format(withdraw_amount, commision.balance, user_id)
            return False

        with transaction.atomic():
            commision.balance -= withdraw_amount
            commision.sum_payed_amount += withdraw_amount
            commision.save()
    except Exception as e:
        from account.scripts.tbk_alipay_send_run import log
        log( "withdraw exception" + e.message)
        return False
    return True


# 根据user_id，从TkUser表中获取被其推荐的二级代理列表，
# 将各二级代理的balance归零，并转移至已提现金额。
# 即无实际转账、仅体现为数据库更新。
def withdraw_agent_commision(user_id):
    sub_agent_list = TkUser.objects.filter(inviter_id=user_id)
    for sub_agent in sub_agent_list:
        try:
            sub_agent_commision = AgentCommision.objects.get(user_id=sub_agent.user_id)
            with transaction.atomic():
                amount = cut_decimal(sub_agent_commision.balance, 2)
                # 直接置0,舍弃分位之后的
                sub_agent_commision.balance = 0
                sub_agent_commision.sum_payed_amount += amount
                sub_agent_commision.save()
        except Exception as e:
            from account.scripts.tbk_alipay_send_run import log
            log("with_draw_subagent_commision error:" + e.message + " sub_agent_id:" + str(sub_agent.user_id))
            continue