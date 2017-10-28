# coding=utf-8
__author__ = 'mingv'

import datetime
import json
from copy import deepcopy
import time
import requests

# from blinker import signal

from django.http.response import HttpResponse
from django.core.cache import cache
from rest_framework.generics import ListAPIView
from rest_framework_jwt.serializers import User
from rest_framework_mongoengine import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from wx_bot.models.contact_models import Host, GroupContact
# from bot_api.settings import tbk_name, tbk_push_url, REMOTE_BOT_SERVER

from account.models.commision_models import AlipayAccount, Commision
from account.serializers.agent_serializers import AlipayAccountSerializer, CommisionSerializer




"""
对用户所绑定的支付宝账户 进行查询,修改和删除 
adam : 并没有办法删除
done at 14:40
"""
class AlipayAccountView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlipayAccountSerializer
    def get_object(self):
        try:
            user_id = str(self.request.user.id)
            # 额?啥意思
            if 'user_id' in self.request.data.keys():
                if user_id != self.request.data['user_id']:
                    return Response({'data': "user id error", 'retCode': 400}, status=status.HTTP_400_BAD_REQUEST)
            account = AlipayAccount.objects.get(user_id=user_id)

            return account
        except AlipayAccount.DoesNotExist:
            return None
        except Exception as e:
            raise Response({'data': self.request.method + e.message, 'retCode': 400},
                           status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({'data': '', 'retCode': 404}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(instance)
        return Response({'data': serializer.data, 'retCode': 200}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance is None:
            return Response({'data': '', 'retCode': 400}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'data': serializer.data, 'retCode': 200}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({'data': '', 'retCode': 204}, status=status.HTTP_204_NO_CONTENT)
        self.perform_destroy(instance)
        return Response({'data': '', 'retCode': 204}, status=status.HTTP_204_NO_CONTENT)


"""
绑定支付宝账户
done at 14:40
"""
class BindingAlipayAccountView(APIView):
    def post(self, request):
        try:
            AlipayAccount.objects.create(
                user_id=str(request.user.id),
                alipay_id=request.data.get('alipay_id'),
                alipay_name=request.data.get('alipay_name'),
                identity_num=request.data.get('identity_num'),
                phone_num=request.data.get('phone_num')
            )
        except Exception as e:
            return Response({'data': 'Binding error:' + e.message, 'retCode': 400},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'data': 'success', 'retCode': 200}, status=status.HTTP_200_OK)


"""
获取淘宝客账户
"""
class GetCommision(ListAPIView):
    serializer_class = CommisionSerializer

    def get(self, request):
        try:
            user_id = request.user.id
            commision = Commision.objects.get(user_id=str(user_id))
            serializer = self.get_serializer(commision)
        except Exception as e:
            return Response({'data': 'query error' + e.message, 'retCode': 400},
                            status=status.HTTP_400_BAD_REQUEST)
        print serializer.data
        return Response({'data': serializer.data, 'retCode': 200}, status=status.HTTP_200_OK)








'''
================待定区=======================
'''

"""
新扫码登录过的淘宝客用户数量
接口给管理员专用
todo:传值需要起始时间和结束时间
             根据迁移后的模型进行更改
"""
# class NewUserCount(APIView):
#     def get(self, request):
#         user_list = User.objects.filter(date_joined__gte='2017-06-10', date_joined__lte='2017-06-27')
#         i = 0
#         for user in user_list:
#             id = user.id
#             host_list = Host.objects.filter(md_user_id=str(id))
#
#             if len(host_list) > 0:
#                 i += 1
#
#         return Response({'data': i})



'''
================停用区=======================
'''

''' 
判断用户是否打开搜索功能
停用
 '''
# @api_view(['get'])
# @permission_classes((AllowAny,))
# def is_search_func_openned(request):
#     try:
#         username = request.GET.get('username', None)
#         md_user_id = User.objects.get(username=username).id
#         rule_list = RuleBase.objects.filter(__raw__={"md_user_id": str(md_user_id)})
#
#         for rule in rule_list:
#             if isinstance(rule.trigger, RegexTrigger):
#                 if rule.trigger.pattern.find(u"找买") != -1:
#                     return Response(json.dumps({'data': 1}), status=status.HTTP_200_OK)
#                 else:
#                     continue
#
#         return Response(json.dumps({'data': 0}), status=status.HTTP_200_OK)
#     except Exception as e:
#         Response(json.dumps({'data': 'exception:{0}'.format(e.message)}), status=status.HTTP_200_OK)


'''
    获取福利群列表
    似乎没用- -
'''
# class TbkGroupList(APIView):
#     def get(self, request):
#         md_user_id = str(request.user.id)
#         group_list = GroupContact.objects.no_dereference().filter(md_user_id=md_user_id)
#         agent_group_list = []
#         for group in group_list:
#             if tbk_name in group.nick_name:
#                 agent_group_list.append(group)
#         return Response({'retCode': 200, 'data': GroupContactSerializer(agent_group_list, many=True).data})


'''
    绑定pid
    逻辑已转移至broadcast
'''
# class UpdatePidView(APIView):
#     def post(self, request):
#         pid = request.data['pid']
#         md_user_id = request.user.id
#         user = User.objects.get(id=md_user_id)
#         user.first_name = pid
#         user.save()
#         return Response({'retCode': 200, 'data': 'success'}, status=status.HTTP_200_OK)


''' 
通过uuid查询host
冗余功能 ,停用
'''
# @api_view(['get'])
# @permission_classes((AllowAny,))
# def get_agent_host_by_uuid(request, md_user_id):
#     """
#     http://{{host}}/api/controller/ag/1069?timeout=false&uuid=gZF8miqrkksZ9mrRk7mc
#     :param request:
#     :param md_user_id:
#     :return:
#     """
#     try:
#         user = User.objects.get(id=int(md_user_id))
#         start_time = datetime.datetime.now()
#         timeout = request.GET.get('timeout', 'false')
#         uuid = request.GET.get('uuid', '')
#
#         if uuid == '':
#             return Response({'status': "uuid is empty"}, status=status.HTTP_200_OK)
#
#         while True:
#             r = requests.get(REMOTE_BOT_SERVER + "/is-uuid-login?qr-uuid=" + uuid, timeout=10)
#             if r.status_code != 200:
#                 return Response({'status': "remote bot server ret code is not 200:{0}".format(r.status_code)},
#                                 status=status.HTTP_200_OK)
#
#             ret_json = json.loads(r.text)
#             ret_code = 1 if ret_json['ret'] == "1" else 0
#
#             # 如果timeout为false，则立马返回,不进行等待
#             if timeout == 'false' or ret_code == 1:
#                 return Response({'status': ret_code, 'name': ret_json['name']}, status=status.HTTP_200_OK)
#
#             if (datetime.datetime.now() - start_time).seconds > 120:
#                 # 超时status为 -1
#                 return Response({'status': -1}, status=status.HTTP_200_OK)
#
#             time.sleep(1)
#     except Exception as e:
#         return Response({'status': "exception occurred:{0}".format(e.message)}, status=status.HTTP_200_OK)


''' 
host登录则发送bearychat通知
停用
'''
# @agent_log_in_signal.connect
# def host_login(sender, **kwargs):
#     host = kwargs.get('host')
#
#     # Send bearychat msg
#     data = {
#         'text': 'taobao agent Host login, nick_name=%s ' % (host.get_nick_name_emoji_unicode()),
#     }
#     requests.post(
#         'https://hook.bearychat.com/=bw8NI/incoming/8f79b59004f557008f22039ca9623ba2',
#         json=data
#     )


''' 
通过uuid查询host
冗余功能 ,停用
'''
# class GetAgentHostByUUid(APIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request, md_user_id):
#         bot = AsyncWxBot(md_user_id)
#         uuid = request.query_params.get('uuid')
#         bot.login(uuid=uuid)
#         host = Host.objects.get(id=bot.bot_info.host_id)
#         agent_log_in_signal.send(
#             'async_bot',
#             host=host
#         )
#         return Response({'data': HostSerializer(host).data}, status=status.HTTP_200_OK)


''' 在BotService中的接口为
    bot_controller_urls = [
    ...

    停用:
    url(r'^tbgroup/([a-zA-Z0-9-_]+)/', TaobaoGroupView.as_view()),
    url(r'^refresh-tbgroup', RefreshGroupView.as_view()),
    url(r'^ag/([a-zA-Z0-9-_]+)/', get_agent_host_by_uuid),
    url(r'^binding-pid', UpdatePidView.as_view()),
    url(r'^tbgroup-list', TbkGroupList.as_view()),
]
    '''

'''
群规则相关, 目前停用.
'''


'''
刷新所有群规则
'''
# class refreshAllGroup(APIView):
#     def get(self, request):
#         pushTime_list = PushTime.objects.filter()
#         for pushTime in pushTime_list:
#             print 'pushTime.md_user_id: ' + str(pushTime.md_user_id) + ' time:' + str(pushTime.interval_time)
#             refreshGroup(pushTime.md_user_id)
#         return Response({'retCode': 200, 'data': 'success'})


'''
针对某用户 刷新群规则
'''
# class TaobaoGroupView(APIView):
#     permission_classes = (AllowAny,)
#     def get(self, request, host_id):
#         md_user_id = str(request.user.id)
#         group_list = GroupContact.objects.filter(host=host_id)
#         list(group_list)
#         agent_group_list = []
#
#         for group in group_list:
#             if tbk_name in group.nick_name and group.member_count > 10:
#                 agent_group_list.append(group)
#
#         for agent_group in agent_group_list:
#             try:
#                 validate_agent_rule(md_user_id, agent_group, len(agent_group_list))
#             except Exception, e:
#                 print e
#                 continue
#         return Response({'retCode': 200, 'data': 'success'})


'''
刷新群规则的接口
'''
# class RefreshGroupView(APIView):
#     def get(self, request):
#         md_user_id = str(request.user.id)
#         refreshGroup(md_user_id)
#         return Response({'retCode': 200, 'data': 'success'})


'''
刷新群规则
'''
# def refreshGroup(md_user_id):
#     # 删除群名不再是淘宝客的规则
#     del_changed_group_name(md_user_id)
#     host_list = Host.objects.filter(md_user_id=md_user_id)
#     agent_group_list = []
#     # 单个机器人的最大发单群数量
#     max_send_group_count = 0
#     for host in host_list:
#         group_list = GroupContact.objects.filter(host=host)
#         # 单个机器人的发单群数量
#         host_agent_group_list = []
#         list(group_list)
#         for group in group_list:
#             print group.nick_name
#             print str(group.member_count )
#             if tbk_name in group.nick_name and group.member_count > 10 and group.user_name != '':
#                 host_agent_group_list.append(group)
#                 agent_group_list.append(group)
#         if len(host_agent_group_list) > max_send_group_count:
#             max_send_group_count = len(host_agent_group_list)
#
#     for agent_group in agent_group_list:
#         try:
#             validate_addgroup_greet_rule(md_user_id, agent_group)
#             validate_agent_rule(md_user_id, agent_group, max_send_group_count)
#         except Exception, e:
#             print e
#             continue


''' 删除所有群名不再含有福利社关键字的淘客群规则 '''
# def del_changed_group_name(md_user_id):
#     rule_list = RuleBase.objects.filter(rule_type='tbk_agent', md_user_id=md_user_id, hidden=True)
#     for rule in rule_list:
#         group = rule.group_list[0]
#         if u'福利社' not in group.nick_name or group.member_count <= 10 or group.user_name == '':
#             rule.delete()


''' 判断是否新建了加群后的欢迎语'''
# def validate_addgroup_greet_rule(md_user_id, group):
#     rule_list = RuleBase.objects.filter(md_user_id=md_user_id, group_list=group, rule_name='tk_greet',
#                                         rule_type='access_group')
#     if len(rule_list) == 0:
#         trigger = AddGroupTrigger.objects.create()
#         action = ReplyTextAction.objects.create(target='from_user', msg='欢迎进群，这里是天猫优惠券的集中发放地，为大家省钱是我义不容辞的责任！')
#
#         RuleBase.objects.create(rule_name='tk_greet', rule_type='access_group', md_user_id=md_user_id,
#                                 group_list=[group],
#                                 action_list=[action], trigger=trigger, classify='reply_text', hidden=False
#                                 )


''' 判断是否存在此群的淘宝客规则，不存在则新建 '''
# def validate_agent_rule(md_user_id, group, list_len):
#     user = User.objects.get(id=md_user_id)
#     username = user.username
#     pid = user.first_name
#     # 根据每个机器人的福利群数量动态计算发言间隔
#     try:
#         pushTime = PushTime.objects.get(md_user_id=md_user_id)
#     except PushTime.DoesNotExist:
#         pushTime = PushTime.objects.create(md_user_id=md_user_id)
#     time_interval = pushTime.interval_time
#     if time_interval < 5:
#         pushTime.interval_time = 5
#         pushTime.save()
#     # safe_interval = list_len * 3
#     #
#     # if time_interval < safe_interval:
#     #     time_interval = safe_interval
#     #     pushTime.interval_time = time_interval
#     #     pushTime.save()
#     begin_time = pushTime.begin_time
#     end_time = pushTime.end_time
#     try:
#         rule = RuleBase.objects.get(rule_type='tbk_agent', md_user_id=md_user_id, group_list=group, hidden=True)
#         trigger = rule.trigger
#         trigger.cycle = time_interval * 60
#         trigger.set_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
#         trigger.save()
#         # 只对已激活群设置规则发单
#         if '' == group.user_name and rule.isValid == True:
#             rule.isValid = False
#         elif group.user_name != '' and rule.isValid == False:
#             rule.isValid = True
#         extra_context_data = rule.extra_context_data
#         extra_context_data['begin_time'] = begin_time
#         extra_context_data['end_time'] = end_time
#         rule.extra_context_data = extra_context_data
#         rule.save()
#     except RuleBase.DoesNotExist:
#         trigger = PeriodicTimeTrigger.objects.create(set_time=datetime.datetime.now() + datetime.timedelta(seconds=20),
#                                                      cycle=(time_interval * 60))
#         action = ComplexWebRequestAction.objects.create(url=tbk_push_url,
#                                                         fields={'gid': 'gid', 'pid': 'pid', 'hid': 'host',
#                                                                 'username': 'username', 'begin_time': 'begin_time',
#                                                                 'end_time': 'end_time'})
#         rule = RuleBase.objects.create(
#             rule_name='代理规则', rule_type='tbk_agent', md_user_id=md_user_id, group_list=[group],
#             action_list=[action], trigger=trigger, classify='tbk_agent',
#             hidden=True, extra_context_data={'pid': pid, 'gid': str(group.id), 'host': str(group.host.id),
#                                              'username': username, 'begin_time': begin_time, 'end_time': end_time})


'''
判断用户距上一次发单时间是否满足发单间隔, 返回的ret值为0或1
整合进taobaoke_views.py, 停用
'''
# @permission_classes((AllowAny,))
# def is_push(request):
#     if request.method == "GET":
#         try:
#             username = request.GET.get('username', None)
#             wx_id = request.GET.get('wx_id', None)
#             md_user_id = User.objects.get(username=username).id
#             try:
#                 user_pt = PushTime.objects.get(md_user_id=str(md_user_id))
#             except PushTime.DoesNotExist:
#                 user_pt = PushTime.objects.create(md_user_id=str(md_user_id))
#             push_interval = user_pt.interval_time
#
#             if username is None or wx_id is None:
#                 return HttpResponse(json.dumps({'data': 'error args:username or wx_id is None', 'ret': 0}),
#                                     status=status.HTTP_200_OK)
#
#             cache_key = username + '_' + wx_id + '_last_push'
#             cache_time_format = "%Y-%m-%d %H:%M:%S"
#
#             cur_time = datetime.datetime.now()
#             # 上一次推送的时间
#             last_push_time = cache.get(cache_key)
#             if last_push_time is None:
#                 is_within_interval = True
#             else:
#                 dt_last_push_time = datetime.datetime.strptime(last_push_time, cache_time_format)
#                 is_within_interval = dt_last_push_time + datetime.timedelta(minutes=push_interval) <= cur_time
#
#             dt_begin_pt = datetime.datetime.strptime(user_pt.begin_time.replace('24:00', '23:59'), '%H:%M')
#             dt_end_pt = datetime.datetime.strptime(user_pt.end_time.replace('24:00', '23:59'), '%H:%M')
#
#             if dt_begin_pt.time() < cur_time.time() < dt_end_pt.time() and is_within_interval:
#                 ret_code = 1
#                 cache.set(cache_key, datetime.datetime.strftime(cur_time, cache_time_format), 3600 * 10)
#             else:
#                 ret_code = 0
#
#             return HttpResponse(
#                 json.dumps(
#                     {
#                         'data':
#                             'cur_time:{0}, begin_time:{1}, end_time:{2}, last_push_time:{3}'.format(
#                                 cur_time.time().strftime('%H:%M'),
#                                 user_pt.begin_time,
#                                 user_pt.end_time,
#                                 last_push_time
#                             ),
#                         'ret': ret_code
#                      }
#                 ), status=status.HTTP_200_OK)
#
#         except Exception as e:
#             return HttpResponse(json.dumps({'data': 'exception:{0}'.format(e.message), 'ret': 0}), status=status.HTTP_200_OK)


'''
检查是否每个用户都存在UserConfig对象,若无则创建.
并未返回实质内容.
UserConfig模型被抛弃
'''
# todo
# class CheckAllUserConfig(APIView):
#     def get(self, request):
#         user_list = User.objects.filter()
#         for user in user_list:
#             try:
#                 userconfig = UserConfig.objects.get(md_user_id=str(user.id))
#             except UserConfig.DoesNotExist:
#                 print 'username:' + user.username + ' id:' + str(user.id) + ' does not exsit'
#                 UserConfig.objects.create(username=user.username, md_user_id=str(user.id), email=user.email)
#         return Response({'data': 'success'})


'''
    设置时间间隔
    转移到注册登录模块, 李正龙在处理
'''
# class setPushTimeView(APIView):
#     def post(self, request):
#         md_user_id = str(request.user.id)
#         interval_time = int(request.data.get('interval_time', 5))
#         begin_time = request.data.get('begin_time')
#         end_time = request.data.get('end_time')
#         try:
#             pushtime = PushTime.objects.get(md_user_id=md_user_id)
#             pushtime.interval_time = interval_time
#             pushtime.begin_time = begin_time
#             pushtime.end_time = end_time
#             pushtime.save()
#         except PushTime.DoesNotExist:
#             pushtime = PushTime.objects.create(md_user_id=md_user_id,
#                                                interval_time=interval_time, begin_time=begin_time, end_time=end_time)
#
#         refreshGroup(md_user_id)
#         return Response({'retCode': 200, 'data': PushTimeSerializer(pushtime).data})


# class getPushTimeView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = PushTimeSerializer
#
#     def get_object(self):
#         mid = str(self.request.user.id)
#         try:
#             pushTime = PushTime.objects.get(md_user_id=mid)
#         except PushTime.DoesNotExist:
#             pushTime = PushTime.objects.create(md_user_id=mid)
#         return pushTime