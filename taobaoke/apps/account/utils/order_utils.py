# coding=utf-8
from math import floor

from django.contrib.auth.models import User
from account.utils.user_utils import get_ad_id
from broadcast.models.user_models import  Adzone

__author__ = 'mingv'

'''
根据用户,获取该用户的所有订单
'''
def get_order_list_by_user(user, order_status, enter_account):
    from account.models.order_models import Order

    ad_id = Adzone.objects.filter(tkuser__user_id=str(user.id)).first().pid.split("_")[3]
    order_list = Order.objects.filter(ad_id=ad_id, order_status=order_status, enter_account=enter_account)
    return order_list


'''
被接口OrderCommisionView调用,
获取所有用户所有未结算订单
'''
def get_all_order():
    user_list = User.objects.filter(is_staff=False, last_login__isnull=False)
    from account.models.order_models import Order
    from account.serializers.order_serializers import OrderSerializer
    user_order_data = []
    for user in user_list:
        user_id = str(user.id)

        ad_id = get_ad_id(user.username)
        order_list = Order.objects.filter(ad_id=ad_id, order_status=u'订单结算', enter_account=False)
        user_order = {'id':user_id,'username':user.username,'order_list':OrderSerializer(order_list,many=True).data}
        user_order_data.append(user_order)
    return user_order_data




'''
==================停用=======================
'''

'''
根据ad_id获取手机号username
停用,整合数据库后直接通过数据库查询.
'''
# def get_username(ad_id):
#     """
#     根据ad_id获取手机号username
#     :param ad_id:
#     :return:
#     """
#     try:
#         textmod = {'adzone_id': ad_id}
#         textmod = urllib.urlencode(textmod)
#         req = urllib2.Request(url='%s%s%s' % (tbk_getusername_url, '?', textmod))
#         res = urllib2.urlopen(req)
#         user_info = res.read()
#         if (user_info != None):
#             username = (json.loads(user_info)).get('user').get('username')
#         return username
#     except Exception, e:
#         print '##get_username error:'+str(ad_id)
#         traceback.print_exc()
#         return None


"""
计算订单佣金总量
似乎已停用
"""
# def cal_sum_commision():
#     """
#     计算订单佣金总量
#     :return:
#     """
#     user_list = User.objects.all()
#     from account.models.commision_models import Commision
#     from account.models.order_models import Order
#     for user in user_list:
#         user_id = str(user.id)
#         try:
#             commision = Commision.objects.get(user_id=user_id)
#         except Commision.DoesNotExist:
#             commision = Commision.objects.create(user_id=user_id)
#         ad_id = get_ad_id(user.username)
#         order_list = Order.objects.filter(ad_id=ad_id, order_status=u'订单结算')
#         sum_earning_amount = 0
#         with transaction.atomic():
#             for Order in order_list:
#                 pay_amount = Order.pay_amount
#                 sum_earning_amount += pay_amount * commision.commision_rate
#                 Order.enter_account = True
#                 Order.save()
#             new_commision = sum_earning_amount - commision.sum_earning_amount
#             commision.sum_earning_amount = sum_earning_amount
#             commision.save()
#
#             if(new_commision > 0):
#                 post(user_id, new_commision, True, 'batch_update_about_many_orders', 'order_commision')

'''
计算一级佣金, 转移至commision_utils
'''
# def cal_new_commision():
#     """
#     计算订单佣金增量
#     :return:
#     """
#     user_list = User.objects.filter(is_staff=False, last_login__isnull=False)
#     from account.models.commision_models import Commision
#     from account.models.order_models import Order
#     for user in user_list:
#         md_user_id = str(user.id)
#         try:
#             commision = Commision.objects.get(md_user_id=md_user_id)
#         except Commision.DoesNotExist:
#             commision = Commision.objects.create(md_user_id=md_user_id)
#         ad_id = get_ad_id(user.username)
#         if ad_id is None:
#             continue
#         order_list = Order.objects.filter(ad_id=ad_id, order_status=u'订单结算', enter_account=False)
#         new_earning_amount = 0
#
#         with transaction.atomic():
#             for Order in order_list:
#                 pay_amount = Order.pay_amount
#                 order_commision = pay_amount * commision.commision_rate
#                 new_earning_amount += order_commision
#                 Order.enter_account = True
#                 Order.save()
#                 post(md_user_id, order_commision, True, Order.order_id, 'order_commision')
#
#             commision.sum_earning_amount += new_earning_amount
#             commision.balance += new_earning_amount
#             commision.save()


'''
判断账户可提现金额是否大于申请转账金额
转移至commision_utils
'''
# def tbk_commission_withdraw(md_user_id, withdraw_amount):
#     """
#     淘宝客提现操作
#     :param md_user_id:用户id(string)
#     :param withdraw_amount: 提现总额(float)
#     :return: 提现操作结果 True-成功 False-失败
#     """
#     try:
#         commission = Commision.objects.get(md_user_id=md_user_id)
#         if withdraw_amount > commission.balance:
#             print "withdraw error:withdraw_amount is greater than balance->" \
#                   "amount:{0},balance:{1},id:{2}".format(withdraw_amount, commission.balance, md_user_id)
#             return False
#
#         with transaction.atomic():
#             commission.balance -= withdraw_amount
#             commission.sum_payed_amount += withdraw_amount
#             commission.save()
#     except Exception as e:
#         # TODO: 专门记录在一个logger里头比较好
#         print "withdraw exception" + e.message
#         return False
#     return True


'''
根据手机号获取adzone数据序列
转移至user_utils
'''
# def get_ad_zone(key, value):
#     """
#     获取adzone序列,
#     """
#     try:
#         if key == 'username':
#             adzone = Adzone.objects.get(tkuser__user__username=value)
#         elif key == 'adzone_id':
#             adzone = Adzone.objects.get(pid__contains=adzone_id)
#         return AdzoneSerializer(adzone).data
#
#     except Exception, e:
#         print '##get_ad_zone error:'+str(value)
#         print e
#         # traceback.print_exc()
#         return None
'''
根据手机号获取ad_id
转移至user_utils
'''
# def get_ad_id(username):
#     """
#     根据手机号获取ad_id
#     :param username:
#     :return:
#     """
#     try:
#         ad_zone = get_ad_zone('username', username)
#         ad_id = ad_zone['pid'].split('_')[3]
#         return ad_id
#     except Exception, e:
#         return None


'''
保留两位小数
转移至common_utils
'''
# def cut_decimal(num_to_cut, keep_length):
#     c = 10**keep_length
#     num_to_cut *= c
#     return floor(num_to_cut)/c