# coding: utf-8
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from broadcast.models.entry_models import Product
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
import json
import requests
import urllib
from datetime import datetime
from broadcast.utils import OSSMgr
from broadcast.utils.sql_utils import SQLHandler


class GetProducts(View):

    @csrf_exempt
    def post(self, request):
        req_dict = json.loads(request.body)
        products_list = []
        item_id = req_dict.get('item_id')
        if item_id:
            for p in  list(Product.objects.filter(item_id__contains=item_id)):
                p_dict = p.__dict__
                p_dict.pop('_state')
                p_dict['create_time'] = p_dict['create_time'].strftime("%Y-%m-%d %H:%M:%S")
                p_dict['last_update'] = p_dict['last_update'].strftime("%Y-%m-%d %H:%M:%S")
                products_list.append(p_dict)
        return HttpResponse(json.dumps({'data':{'products': products_list}}))
    # todo: 等彩云搞定之后用这个


class EditProduct(View):
    def get(self,request):
        product_id = request.GET.get('product_id')
        p = Product.objects.get(item_id=product_id)
        text=None
        img_list=[]
        if p.broadcast_text:
            text = p.broadcast_text
        if p.broadcast_img:
            img_list = json.loads(p.broadcast_img)
        return render_to_response('edit_product.html', {'product_id':product_id, 'title':p.title, 'broadcast_text':text, 'broadcast_img':img_list})
    def post(self,request):
        product_id = request.POST.get('product_id')
        text = request.POST.get('text')
        imgs1 = request.FILES.get('imgs1')
        imgs2 = request.FILES.get('imgs2')
        imgs3 = request.FILES.get('imgs3')
        imgs4 = request.FILES.get('imgs4')
        p = Product.objects.get(item_id=product_id)
        img_list = p.broadcast_img
        if not img_list:
            img_list=[]
        else:
            img_list = json.loads(img_list)
        for img in [imgs1, imgs2, imgs3, imgs4]:
            if img:
                # if type(img)
                oss = OSSMgr()
                oss.bucket.put_object(img.name.encode('utf-8'), img.file)
                monthday = str(datetime.now().month) + str(datetime.now().day)
                img_url = 'http://md-oss.di25.cn/{0}{1}?x-oss-process=image/quality,q_65'.format(monthday, urllib.quote(img.name.encode('utf-8')))
                img_list.append(img_url)
        p.broadcast_text=text
        p.broadcast_img=json.dumps(img_list)
        p.save()
        return HttpResponseRedirect('operate/operating-edit/?product_id={}'.format(p.item_id))


class DeleteProductImg(View):
    def post(self, request):
        req_dict = json.loads(request.body)
        product_id = req_dict.get('product_id')
        index = req_dict.get('index')
        p = Product.objects.get(item_id=product_id)
        imgs = json.loads(p.broadcast_img)
        del imgs[index-1]
        p.broadcast_img = json.dumps(imgs)
        p.save()
        return HttpResponseRedirect('operate/operating-edit/?product_id={}'.format(product_id))


class RefreshProducts(View):
    def get(self, request):
        action = 'restart'
        if action:
            target = 'http://s-prod-07.qunzhu666.com:9001/index.html?processname=taobaoke%3Afetch_lanlan&action={}'.format(action)
            requests.get(target, headers={"Authorization": "Basic bWF4d2VsbDptYXh3ZWxsX2FkbWlu", "connection": "close"})
            return HttpResponse()


class ChangePushStatus(View):
    def get(self, request):
        action = request.GET.get('action')
        if action:
            target = 'http://s-prod-07.qunzhu666.com:9001/index.html?processname=taobaoke%3Asend_request&action={}'.format(action)
            requests.get(target, headers={"Authorization": "Basic bWF4d2VsbDptYXh3ZWxsX2FkbWlu", "connection": "close"})
            return HttpResponse()


class ParseImg(View):
    def post(self,request):
        cur_file = request.FILES.get('global-img')
        oss = OSSMgr()
        monthday = str(datetime.now().month) + str(datetime.now().day)
        oss.bucket.put_object(monthday+cur_file.name.encode('utf-8'), cur_file.file)
        img_url = 'http://md-oss.di25.cn/{0}{1}?x-oss-process=image/quality,q_65'.format(monthday,urllib.quote(cur_file.name.encode('utf-8')))
        return HttpResponse(json.dumps({'data':img_url}))


class SelectCate(View):
    def get(self, request):
        cur_cate = cache.get('mmt_select_cate')
        if cur_cate is None:
            cur_cate = []
            cache.set('mmt_select_cate', cur_cate, 60*60*24*3)
        sql_sentence = "SELECT DISTINCT cate FROM broadcast_product"
        all_cate = [cate[0] for cate in SQLHandler.execute(sql_sentence)]
        all_cate.remove(None)
        ret_dict = {
            'cur_cate':cur_cate,
            'all_cate': all_cate
        }
        return HttpResponse(json.dumps({'data': ret_dict}))
    def post(self, request):
        try:
            req_dict = json.loads(request.body)
        except ValueError:
            return HttpResponse(json.dumps({'data': 'Wrong JSON format.'}))
        cate = req_dict.get('mmt_select_cate')
        cache.set('mmt_select_cate', cate, 60*60*24*3)
        return HttpResponse(json.dumps({'data': 'success'}))

class QueryOrder(View):
    def post(self, request):
        req = json.loads(request.body)
        order_id = req.get('order_id')
        if order_id is None:
            return HttpResponse(json.dumps({'data':'无此订单。'}))
        sql_sentence = "SELECT * FROM `wxuser_order_relationship` WHERE order_id={}".format(order_id)
        result = SQLHandler.execute(sql_sentence, True)
        time_format = '%Y-%m-%d %H:%M:%S'
        resp_list=[]
        for r in result:
            r['last_update_time'] = r['last_update_time'].strftime(time_format)
            r['create_time'] = r['create_time'].strftime(time_format)
            r['click_time'] = r['click_time'].strftime(time_format)
            resp_dict = {
                '订单ID': r['order_id'],
                '订单状态': r['order_status'],
                '创建时间': r['create_time'],
                '最近更新': r['last_update_time'],
                '商品ID': r['good_id'],
                '商品名称': r['good_info'],
                '商品数量': r['good_num'],
                '商品原价': r['good_price'],
                '付款金额': r['pay_amount'],
                '结算时间': r['earning_time'],
                '确认金额': r['balance_amount'],
                '佣金比例': r['commision_rate'],
                '佣金金额': r['commision_amount'],
                '代理佣金比例': r['show_commision_rate'],
                '代理佣金金额': r['show_commision_amount'],
                '代理用户': r['user_id'],
                '代理帐号': r['username'],
                '代理微信': r['nickname'],
                '是否入账': bool(r['enter_account']),
            }
            resp_list.append(resp_dict)
        return HttpResponse(json.dumps({'data': resp_list}))
