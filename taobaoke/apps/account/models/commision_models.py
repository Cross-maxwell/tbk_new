# coding=utf8
from django.db import models
from django.contrib.auth.models import User

__author__ = 'mingv'

class Account(models.Model):
    '''
     在user_model中监听User创建.
     通过 account.scripts.clearing_account.py 脚本维护
        API :  order_views.PostingAccount
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 待提现佣金
    amount = models.FloatField('金额', default=0, null=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class AlipayAccount(models.Model):
    """
    和用户绑定的支付宝账户
    通过API - BindingAlipayAccountView 创建
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alipay_id = models.CharField('支付宝账户', max_length=40)
    alipay_name = models.CharField('支付宝用户姓名', max_length=10)
    identity_num = models.CharField('身份证号码', max_length=18)
    #和支付宝绑定的手机号码
    phone_num = models.CharField('手机号码', max_length=11)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class AccountFlow(models.Model):
    '''
    账户流水
     通过 account.scripts.clearing_account.py 脚本维护
        API :  order_views.PostingAccount
    '''
    user_id = models.CharField('用户ID', max_length=16)
    # 代理佣金
    # 淘宝客佣金
    type = models.CharField('结算类型', max_length=16)
    # 入账 True
    # 出账，提现 False
    in_or_out = models.BooleanField('出入账', default=True, null=False)
    amount = models.FloatField('金额', default=0, null=False)
    order_id = models.CharField('订单ID', max_length=50)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class Commision(models.Model):
    """
    每个淘宝客单独的账户情况
    在user_model中监听User创建.
    通过order_views.py 中的AutoCalCommisionView 进行维护
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 待提现佣金
    balance = models.FloatField('账户金额', default=0)

    # 总结算金额
    sum_earning_amount = models.FloatField('总佣金', default=0)
    sum_payed_amount = models.FloatField('已提现金额', default=0)

    # 账户有效性
    is_valid = models.BooleanField(default=True, null=False)
    # 每个人特有的佣金比例
    commision_rate = models.FloatField(default=0.15)
    # pid
    # pid = models.CharField('pid',  null=True, max_length=64)
    #
    # ad_id = models.CharField('ad_id',  max_length=16, null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class AgentCommision(models.Model):
    """
    淘宝客一级代理商佣金账户
    在user_model中监听User创建.
    ##
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 待提现佣金
    balance = models.FloatField('账户金额', default=0)

    # 总结算金额
    sum_earning_amount = models.FloatField('总佣金', default=0)
    sum_payed_amount = models.FloatField('已提现金额', default=0)

    # 代理佣金比例，一般为5%
    commision_rate = models.FloatField(default=0.05)
    # pid
    # pid = models.CharField('pid',  null=True, max_length=64)
    # # adzoneid
    # ad_id = models.CharField('ad_id',  max_length=16, null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)




