# coding=utf-8

'''
    2017.10.31  19:33 迁移数据至新库
'''
import sys
sys.path.append('/home/adam/mydev/new_taobaoke/taobaoke')

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

import json

from datetime import datetime
from account.models.order_models import Order,AgentOrderStatus
from account.models.commision_models import Account,AccountFlow,AlipayAccount,Commision,AgentCommision
from django.contrib.auth.models import User
from broadcast.models.user_models import TkUser

file_path = '/home/adam/mydev/my_scripts/'

def migrate_order(file='order_json.json'):
    source = os.path.join(file_path, file)
    with open(source,'r') as f:
        data_list = json.loads(f.read())
    for data in data_list:
        data.pop('_id')
        try:
            data['create_time']=datetime.fromtimestamp(data['create_time']['$date']/1000).strftime("%Y-%m-%d %H:%M:%S")
        except KeyError:
            data['create_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            data['last_update_time']=datetime.fromtimestamp(data['last_update_time']['$date']/1000).strftime("%Y-%m-%d %H:%M:%S")
        except KeyError:
            data['last_update_time']=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            data['click_time']=datetime.fromtimestamp(data['click_time']['$date']/1000).strftime("%Y-%m-%d %H:%M:%S")
        except KeyError:
            data['click_time']=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if 'earning_time' in data.keys():
            data['earning_time'] = datetime.fromtimestamp(data['earning_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        try:
            data['user_id']=TkUser.objects.get(adzone__pid__contains=data['ad_id']).user_id
        except TkUser.DoesNotExist:
            continue

        Order.objects.update_or_create(**data)

def migrate_aos(file='aos_json.json'):
    source = os.path.join(file_path, file)
    with open(source,'r') as f:
        data_list = json.loads(f.read())
    for data in data_list:
        AgentOrderStatus.objects.create(**data)

def migrate_account(file='account_json.json'):
    source = os.path.join(file_path, file)
    with open(source,'r') as f:
        data_list = json.loads(f.read())
    for data in data_list:
        try:
            data['user_id']=User.objects.get(username=data['username']).id
            data['create_time'] = datetime.fromtimestamp(data['create_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            data['update_time'] = datetime.fromtimestamp(data['update_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            data.pop('username')
            Account.objects.create(**data)
        except Exception,e:
            print e.message
            print data

def migrate_account_flow(file='account_flow_json.json'):
    source = os.path.join(file_path, file)
    with open(source,'r') as f:
        data_list = json.loads(f.read())
    for data in data_list:
        data['user_id']=User.objects.get(username=data['username']).id
        data['create_time'] = datetime.fromtimestamp(data['create_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        data['update_time'] = datetime.fromtimestamp(data['update_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        data.pop('username')
        AccountFlow.objects.create(**data)

def migrate_alipay_account(file = 'alipay_account_json.json'):
    source = os.path.join(file_path, file)
    with open(source,'r') as f:
        data_list = json.loads(f.read())
    for data in data_list:
        data['user_id'] = User.objects.get(username=data['username']).id
        data['create_time'] = datetime.fromtimestamp(data['create_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        data['update_time'] = datetime.fromtimestamp(data['update_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        data.pop('username')
        AlipayAccount.objects.create(**data)

def migrate_commision(file = 'commision_json.json'):
    source = os.path.join(file_path, file)
    with open(source,'r') as f:
        data_list = json.loads(f.read())
    for data in data_list:
        try:
            data['user_id'] = User.objects.get(username=data['username']).id
            data['create_time'] = datetime.fromtimestamp(data['create_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            data['update_time'] = datetime.fromtimestamp(data['update_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            data.pop('username')
            data.pop('ad_id')
            data.pop('pid')
            Commision.objects.update_or_create(**data)
        except Exception,e:
            print e.message
            print data

def migrate_agent_commision(file='agent_commision_json.json'):
    source = os.path.join(file_path, file)
    with open(source,'r') as f:
        data_list = json.loads(f.read())
    for data in data_list:
        try:
            data['user_id'] = User.objects.get(username=data['username']).id
            data['create_time'] = datetime.fromtimestamp(data['create_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            data['update_time'] = datetime.fromtimestamp(data['update_time']['$date'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            data.pop('username')
            data.pop('ad_id')
            data.pop('pid')
            AgentCommision.objects.create(**data)
        except Exception, e:
            print e.message
            print data



if __name__=="__main__":
    # migrate_order()
    # migrate_aos()
    # migrate_account()
    # migrate_account_flow()
    # migrate_alipay_account()
    # migrate_commision()
    migrate_agent_commision()