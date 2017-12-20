# coding=utf-8
import json

from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from django.views.generic.base import View
from account.utils import account_utils
from django.http import HttpResponse

from account.models.commision_models import AgentCommision
from account.models.order_models import Order
from account.serializers.order_serializers import OrderSerializer
from account.utils.order_utils import get_all_order
from account.utils.common_utils import cut_decimal
from account.utils.user_utils import get_ad_zone, get_ad_id
from broadcast.models.user_models import TkUser


class OrderList(View):
    """
    获取订单列表
    """
    def get(self, request):
        try:
            # sortKey = request.GET.get('sortKey')
            # desc = request.GET.get('desc')
            order_list = getOrderListByUserName(request.user.username)
        except Exception as e:
            return HttpResponse(json.dumps({'data':'Query error:'+e.message}),status=400)
        return HttpResponse(json.dumps({'data': OrderSerializer(order_list, many=True).data}),status=200)


def getOrderListByUserName(username):
    """
    根据手机号获取相应的订单列表
    :param username:
    :return:
    """
    ad_id = get_ad_id(username)
    order_list = Order.objects.filter(ad_id=ad_id)
    return order_list


class GetGoodPv(View):
    """
    获取浏览量
    """
    def get(self, request):
        ad_zone = get_ad_zone('username', request.user.username)
        click_30d = ad_zone['click_30d']
        return HttpResponse(json.dumps({'data': click_30d}),status=200)


class PostingAccount(View):
    """
    提供给第三方调用入账接口
    简版
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        md_user_id = request.GET.get('md_user_id')
        amount = request.GET.get('amount')
        in_or_out = request.GET.get('in_or_out')
        order_id = request.GET.get('order_id')
        type1 = request.GET.get('type')
        account_utils.post(md_user_id, amount, in_or_out, order_id, type1)
        return HttpResponse(json.dumps({'data': 'successful update the data'}), status=200)


class SetBackUpInfoView(View):
    """
    修改二级代理的备注信息
    """
    def post(self, request):
        user_id = request.user.id
        req_dict = json.loads(request.body)
        sub_agent_username = req_dict.get('sub_agent_user', None)
        backup_info = req_dict.get('back_up_info', None)

        try:
            sub_agent_user_id = User.objects.get(username=sub_agent_username).id
        except User.DoesNotExist as e:
            return HttpResponse(json.dumps({'data': "{} user is not exist".format(sub_agent_username)}), status=400)

        # 防止接口被恶意使用, 判断此下级代理是否为该用户下级代理
        try:
            tmp = TkUser.objects.get(user_id=sub_agent_user_id)
        except TkUser.DoesNotExist as e:
            return HttpResponse(json.dumps({'data': "{} userid in tkuser is not exist".format(sub_agent_user_id)}), status=400)

        if not tmp.inviter_id == str(user_id):
            return HttpResponse(json.dumps({'data': "{}'s superior is not you".format(sub_agent_user_id)}), status=400)
        tmp.inviter_backup_info = backup_info
        tmp.save()
        return HttpResponse(json.dumps({'data': "success"}), status=200)


class InviterLastLoginView(View):
    """
    获取下级代理人员列表，显示最后登录时间
    """
    def get(self, request):
        username = request.user.username
        try:
            agent_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse(json.dumps({'error': 'username does not exist'}), status=400)
        sub_agent_list = TkUser.objects.filter(inviter_id=agent_user.id)
        data = []
        for sub_agent in sub_agent_list:
            sa_username = sub_agent.user.username
            last_login = sub_agent.user.last_login
            if sub_agent.user.last_login is not None:
                last_login = format(sub_agent.user.last_login, "%Y-%m-%d %H:%M:%S")
            md_list_json = {'username': sa_username, 'last_login': last_login}
            data.append(md_list_json)
        return HttpResponse(json.dumps({'data': data}), status=200)


class InviterOrderListView(View):
    """
    获取下级代理订单信息，下级代理总赚取佣金，产生总二级佣金
    """
    def get(self, request):
        user_id = request.user.id
        # sort_key = request.GET.get('order-sortKey')
        # desc = request.GET.get('order-desc')
        try:
            agent_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponse(json.dumps({'error': 'username does not exist'}), status=400)
        # 拿到所有下级代理
        sub_agent_list = TkUser.objects.filter(inviter_id=agent_user.id)
        # 下级代理的订单详情列表
        detail_list = []
        # 该用户的总二级佣金
        sum_user_earning = 0
        for sub_agent in sub_agent_list:
            sub_agent_username = sub_agent.user.username
            agent_id = sub_agent.user_id

            # 下级代理的订单列表
            order_list = getOrderListByUserName(sub_agent_username)

            # 下级代理产生的二级佣金
            try:
                sub_agent_commission = AgentCommision.objects.get(user_id=agent_id)
            except AgentCommision.DoesNotExist:
                sub_agent_commission = AgentCommision.objects.create(user_id=agent_id)

            sub_commission_rate = sub_agent_commission.commision_rate
            print
            # 下级代理订单总额
            order_sum_payed = 0
            # 下级代理的佣金
            user_earning = 0

            # 计算上面俩值
            for order in order_list:
                if order.enter_account is True:
                    order_sum_payed += order.pay_amount
                    # 在这里加上计算逻辑，保证结算与显示一致
                    try:
                        order_commision_rate = round(float(order.commision_amount) / order.pay_amount, 2)
                    except ZeroDivisionError:
                        order_commision_rate = 0
                    if order.pay_amount > 500 and order_commision_rate < 0.25:
                        # order_commision = order.pay_amount * order_commision_rate * 0.1
                        user_earning += order.pay_amount * order_commision_rate*0.1
                    else:
                        user_earning += order.pay_amount * sub_commission_rate
                        # order_commision = order.pay_amount * agent_commision.commision_rate

            md_order_json = {
                'username': sub_agent_username,
                'order_list': OrderSerializer(order_list, many=True).data,
                'order_sum_payed': cut_decimal(order_sum_payed, 2),
                'user_earning': cut_decimal(user_earning, 2),
                'sub_agent_balance': cut_decimal(sub_agent_commission.balance, 2),
                'back_up_info': sub_agent.inviter_backup_info
            }

            detail_list.append(md_order_json)
            sum_user_earning += cut_decimal(user_earning, 2)

        data = {'sum_user_earning': sum_user_earning, 'detail_list': detail_list}
        return HttpResponse(json.dumps({'data': data}), status=200)


class OrderCommisionView(View):
    """
    获取所有人的未结算订单
    """
    def get(self, request):
        data = get_all_order()
        return HttpResponse(json.dumps({'data': data}), status=200)



"""
----------------------------------------------停用区----------------------------------------

"""

"""
已被替代,在pub_alimama_data中直接读取数据存库,不再使用接口
"""
# class OrderBatchCreate(generics.CreateAPIView):
#     """
#         批量创建订单
#     """
#     permission_classes = (AllowAny,)
#
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#
#     def create(self, request, *args, **kwargs):
#
#         # all_data = request.data
#         # appid = all_data.get('appid')
#         # time_stamp = all_data.get('time_stamp')
#         # noncestr = all_data.get('noncestr')
#         # jsapi_ticket = all_data.get('jsapi_ticket')
#
#         datas = request.data
#         update_num = 0
#         insert_num = 0
#         for data in datas:
#             try:
#                 order_id = data['order_id']
#                 Order = Order.objects.get(order_id=order_id)
#                 serializer = OrderSerializer(Order, data=data)
#                 if serializer.is_valid():
#                     serializer.save()
#                 print 'update data :' + str(data)
#                 update_num += 1
#             except Order.DoesNotExist:
#                 serializer = self.get_serializer(data=data)
#                 if serializer.is_valid():
#                     serializer.save()
#                 print 'insert data :' + str(data)
#                 insert_num += 1
#             except Exception, e:
#                 print e
#                 continue
#         leave_num = len(datas) - update_num - insert_num
#         return_str = '更新 ' + str(update_num) + ' 条已存在订单数据，插入 ' + str(insert_num) + ' 条新订单数据,有 ' + str(
#             leave_num) + ' 条数据出错'
#         try:
#             cal_new_commision()
#         except Exception,e:
#             send_message(admin_phone,'订单批量插入时入账异常，请关注下次插入时自动计算【群秘】')
#             traceback.print_exc()
#         return Response({'retCode': 200, 'data': return_str})
#
#     def perform_create(self, serializer):
#         serializer.save()

'''
    创建订单
    同OrderBatchCreate, 已被替代.
'''
# class OrderCreate(generics.CreateAPIView):
#     permission_classes = (AllowAny,)
#
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

'''
无引用
'''
# def post(request):
#     from django.http import JsonResponse
#
#     response_data = {'code': 200}
#
#     return JsonResponse(response_data, status=200)


"""
    初始化所有数据
    已停用
"""
# class InitCommisionView(APIView):
#     def get(self, request):
#         user_list = User.objects.filter()
#         for user in user_list:
#             if(user.id == '237'):
#                 print user.id
#             try:
#                 commision = Commision.objects.get(user_id=str(user.id))
#             except Commision.DoesNotExist:
#                 commision = Commision.objects.create(user_id=str(user.id))
#
#             if user.first_name is not None and user.first_name != '':
#                 commision.pid = user.first_name
#             if user.last_name is not None and user.last_name != '':
#                 commision.ad_id = user.last_name
#                 commision.save()

        # return Response({'data':'success'})

'''
计算每个人的佣金, 
维护Commision, Account, AccountFlow
功能放在pub_alimama_push中,接口停用.
'''
# class AutoCalCommisionView(APIView) :
#     def post(self, request):
#         cal_new_commision()
#         return Response({'retCode': 200})


'''
    WTF?
    adam : 不知道啥用
'''
# class AmountView(APIView):
#     def get(self, request):
#         Order_list = Order.objects.all()
#
#     def head(self, request):
#         user_list = User.objects.filter(id__gt=223)
#         i = 0
#         for user in user_list:
#             count = Host.objects.filter(md_user_id=str(user.id)).count()
#             if (count > 0):
#                 print str(user.id)
#                 print user.username
#                 i = i + 1
#         print i
#         return Response({i})