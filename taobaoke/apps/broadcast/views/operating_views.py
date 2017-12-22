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
        products_list = []
        item_id = request.POST.get('item_id')
        if item_id:
            products_list = list(Product.objects.filter(item_id__contains=item_id))
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
            cache.set('mmt_select_cate', json.dumps(cur_cate), 60*60*24*3)
        sql_sentence = "SELECT DISTINCT root_cat_name from broadcast_productcategory"
        all_cate = [cate[0] for cate in SQLHandler.execute(sql_sentence)]
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
