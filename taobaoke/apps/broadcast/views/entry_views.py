# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import random
import re
import time
import datetime
import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup as BS
from urllib import urlopen
### 仅adam本地测试用，部署时此处须更改
# executable_path = '/home/adam/mydev/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'
executable_path = '/home/tk/taobaoke/env_bck/selenium/webdriver/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'

from django.utils import timezone
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from broadcast.models.entry_models import Product, PushRecord
from broadcast.models.user_models import TkUser
from broadcast.views.server_settings import *
from weixin_scripts.post_taobaoke import select

@csrf_exempt
def insert_product(request):
    req_dict = json.loads(request.body)

    key_list = [
        'title', 'desc', 'img_url',
        'cupon_value', 'price', 'cupon_url',
        'sold_qty', 'cupon_left',
    ]
    item_id = re.search('itemId=(\d+)', req_dict['cupon_url']).groups()[0]
    if Product.objects.filter(item_id=item_id).exists():
        p = Product.objects.get(item_id=item_id)
        for key in key_list:
            setattr(p, key, req_dict[key])
        if req_dict['is_finished'] == 'true' or req_dict['cupon_left'] == 0:
            p.available = False
        else:
            p.available = True
        p.save()
        print 'Product updated.'
    else:
        p = Product.objects.create(**{key: req_dict[key] for key in key_list})
    p.refresh_from_db()
    p.assert_available()

    return HttpResponse('Success', status=201)


@csrf_exempt
def insert_product_by_msg(request):
    return HttpResponse('Success', status=201)


def handle_product_from_qq(msg):

    # 商品推送消息可能有多种形式：
    # case1 : 全文有一个链接，链接格式为"https://s.click.taobao.com/……"，打开链接后会跳转到类似cupon_url的页面，
    #                 但url中仅有activity_id,须做进一步跳转获取item_id。                                          最难搞
    # case2 : 全文有两个链接，商品链接形式为"https://s.click.taobao.com/……"，其中没有item_id; 优惠券链接为常规链接，
    #                 其中有activity_id。                                                                                                                   比较难搞
    # case3 : 全文有两个链接，商品链接中包含item_id，优惠券链接中包含activity_id，按照正常逻辑进行处理。
    #                                                                                                                                                                               一般难搞
    #
    # Attention : 目前默认条件-有两个链接时，优惠券链接中包含activity_id。若之后出现优惠券链接会跳转的情况，须再加判断。

    # 预定义正则匹配pattern:
    item_id_pattern = 'item\.htm\?[.\W]*id=(\d*)'
    item_id_pattern_backup = 'itemId=(\d*)'
    activity_id_pattern = 'activity_?[iI]d=([\w\d]*)'
    s_click_pattern = '(https?://s\.click.taobao\.com/[\d\w]*)'


    try:
        driver = webdriver.PhantomJS(executable_path)
        time_for_load = 0   # 等待页面加载完成的时间。具体时长需在服务器中测试确定。

    ### 下面的if…else…用于针对不同的消息类型，获取item_id及activity_id
    # 第一种情形，msg中只有一个链接：
        if len(re.findall('http', msg)) == 1:
            # first_url : 第一层链接，为"https://s.click.taobao.com/……"形式，进入页面后跳转至优惠券页面，其中包含activity_id。
            first_url = re.findall(s_click_pattern, msg)[0]
            driver.get(first_url)
            time.sleep(time_for_load)
            # second_url : 第二层链接，从分享链接跳转，其中包含activity_id
            second_url = driver.current_url
            activity_id = re.findall(activity_id_pattern, second_url)[0]
            # third_url : 第三层链接，从优惠券页面进入商品页面，之后从url中提取item_id
            third_url = driver.find_element_by_class_name('item-detail').get_attribute('href')
            driver.get(third_url)
            # final_url : 最终跳转到的淘宝商品链接，url中包含item_id。
            final_url = driver.current_url
            item_id = re.findall(item_id_pattern, final_url)[0]

        else :
            # activity_id : 活动id，从qq消息中带有的优惠券地址获取，由数字和字母组成
            activity_id = re.findall(activity_id_pattern, msg)[0]
            # item_id : 商品id，从qq消息中带有的下单地址获取，由数字组成
            item_id_list = re.findall(item_id_pattern, msg)

            #针对case2 & case3 , 获取item_id需要一些周折
            if item_id_list != []:
                ### case3，直接匹配item_id
                item_id = item_id_list[0]
            else:
                ### case2，需进入商品链接，待跳转后再获取itemid
                tran_item_url = re.findall(s_click_pattern, msg)[0]
                driver.get(tran_item_url)
                time.sleep(time_for_load)
                try:
                    item_id = re.findall(item_id_pattern, driver.current_url)[0]
                except:
                    item_id = re.findall(item_id_pattern_backup, driver.current_url)[0]

        # cupon_url : 优惠券url，用商品id及活动id拼接
        cupon_url = 'https://uland.taobao.com/coupon/edetail?activityId={0}&itemId={1}&src=xsj_lanlan'.format(
            activity_id, item_id)

        # item_url : 天猫商城商品页，从页面中获取商品的title , image_url
        # 重新赋值，覆盖case1中的赋值。
        item_url = 'https://detail.tmall.com/item.htm?id={}'.format(item_id)

        # 使用BeautifulSoup进行页面解析，抓取title和image_url属性：
        # title : 商品标题，在天猫商品页中位于<h1 data-spm="1000983"中>，生成淘口令的必须参数         补充：已更换爬取的tag。
        # img_url : 商品图片链接，在天猫商品页中位于<img id="J_ImgBooth"中>，生成淘口令的必须参数
        #
        # 注：通过fetch_lanlan抓取的商品img_url和此法所得的不一样，经测试生成淘口令后会引向同一个商品。
        driver.get(item_url)
        try:
            img_url = driver.find_element_by_id('J_ImgBooth').get_attribute('src')
        except:  # 若商品页使用视频介绍，则会在进入页面后加载视频，J_ImgBooth标签会隐藏，故使用BS获取加载前的页面。
            html = urlopen(item_url)
            bs_obj = BS(html,'lxml')
            img_url = 'https://'+bs_obj.find('img',{'id' : 'J_ImgBooth'}).get('src')

        try: # 天猫商品页
            title = driver.find_element_by_class_name('tb-detail-hd').find_element_by_tag_name('h1').text.strip('\r\n\t')
        except: # 淘宝商品页
            title = driver.find_element_by_class_name('tb-main-title').text.strip('\r\n\t')
        ###待实例测试


        # 抓取优惠券信息
        # 优惠券页面为动态加载, 此处用selenium进行采集
        driver.get(cupon_url)
        time.sleep(time_for_load)

        # 若页面中无class="coupons-price"及"sale"的标签，则优惠券已失效 。
        try:
            cupon_value = float(driver.find_element_by_class_name("coupons-price").text.strip(u'\xa5'))
            price = float(driver.find_element_by_class_name("sale").text.strip(u'\xa5'))
            # 销量格式为”XXX笔成交“，将“笔成交”三字去除
            sold_qty = driver.find_element_by_class_name("dealNum").text.strip(u'\u7b14\u6210\u4ea4')
            # 销量可能以“万”字结尾，此处加以处理
            if u'\u4e07' in sold_qty:
                sold_qty = int(float(sold_qty.strip(u'\u4e07')) * 10000) + random.randint(0, 9999)
            else:
                sold_qty = int(sold_qty)
            # 剩余券数未找到可抓取源，鉴于在项目中基本未使用(Product.cupon_left 和 Entry.available 均未使用)，此处手动赋值为1。
            cupon_left = 1

            # fetch_lanlan脚本的运行频率为5分钟一次，比QQ消息传入频率高得多，所以当QQ群中发出产品在我库中存在时，直接跳过而不依照QQ消息更新。
            if Product.objects.filter(item_id=item_id).exists():
                print '库中已存在此商品，本条消息不做存储。'
                p = Product.objects.filter(item_id=item_id).first()
            else:
                p = Product.objects.create(title=title, desc='', img_url=img_url, cupon_value=cupon_value,
                                           price=price, sold_qty=sold_qty, cupon_left=cupon_left,
                                           cupon_url=cupon_url)
                p.save()
                print '商品存储完成。'
            # 向微信群中发送该商品推广信息。
            print '向微信群中推送……'
            select(p)
        except NoSuchElementException:
            print '优惠券已失效。'
            if Product.objects.filter(item_id=item_id).exists():
                p_duplicate = Product.objects.filter(item_id=item_id).first()
                p_duplicate.available = False
                p_duplicate.save()
    except:
        print('商品解析失败，放弃对本条商品的存储')


def handle_qq_msg(kuq_msg):
    #从酷q插件传入的qq群推送商品消息，字符串形式

    # 消息可能为：
    #     1.商品推送，带有"券后"、”下单“、”抢购“等字眼, 且至少有两个链接（其中一个为图片链接）。
    #     2.代理广告或活动预告，有图片和文字，但无上述字眼。
    # 此处仅对商品推送进行处理

    if ("券后" in kuq_msg or ("抢购" in kuq_msg or "下单" in kuq_msg)) and len(re.findall('http', kuq_msg)) > 0:
        print '从QQ群消息导入商品中……'
        handle_product_from_qq(kuq_msg)
    else:
        print '无关消息, 忽略'


@csrf_exempt
def insert_broadcast_by_msg(request):
    print '收到来自QQ群的消息。'
    kuq_msg = request.body

    import thread
    thread.start_new_thread(handle_qq_msg, (kuq_msg,))
    return HttpResponse('Success', status=201)

@csrf_exempt
def push_product(request):
    data = {
        "ret_code": 0,
        "reaction_list": [
        ]
    }

    request_data = json.loads(request.body)
    group_id = request_data['gid']
    host_id = request_data['hid']
    # pid = request_data['pid']
    username = request_data['username']
    push_url = request_data.get('post_url', 'http://s-prod-07.qunzhu666.com:8000/api/platform-api/create-exec/')
    tk_user = TkUser.get_user(username)
    pid = tk_user.adzone.pid

    begin_time = datetime.datetime.strptime(request_data['begin_time'].replace('24:00', '23:59'), '%H:%M')
    end_time = datetime.datetime.strptime(request_data['end_time'].replace('24:00', '23:59'), '%H:%M')

    if not begin_time.time() < datetime.datetime.now().time() < end_time.time():
        data['ret_code'] = -1
        return HttpResponse(json.dumps(data), status=200)

    qs = Product.objects.filter(
        ~Q(pushrecord__group__contains=group_id, pushrecord__create_time__gt=timezone.now() - datetime.timedelta(days=3)),
        available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
    )

    # 用发送过的随机商品替代
    if qs.count() == 0:
        qs = Product.objects.filter(
            available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
        )
        requests.post(
            'https://hook.bearychat.com/=bw8NI/incoming/219689cd1075dbb9b848e4c763d88de0',
            json={'text': '点金推送商品失败：无可用商品, group_id=%s' % group_id}
        )

    for _ in range(50):
        try:
            r = random.randint(0, qs.count() - 1)
            p = qs.all()[r]
            break
        except Exception as exc:
            print "Get entry exception. Count=%d." % qs.count()
            print exc.message

    img_msg = {
        'type': 'img',
        'content': p.get_img_msg(),
        'host_id': host_id,
        'target_id': group_id,
    }

    text_msg = {
        'type': 'text',
        'content': p.get_text_msg(pid),
        'host_id': host_id,
        'target_id': group_id,
    }

    PushRecord.objects.create(entry=p, group=group_id)

    requests.post(push_url, json.dumps(img_msg))
    print "Push img %s to group %s." % (img_msg['content'], img_msg['target_id'])
    # time.sleep(5)
    requests.post(push_url, json.dumps(text_msg))
    print "Push text %s to group %s." % (text_msg['content'], text_msg['target_id'])
    return HttpResponse(json.dumps(data), status=200)


@csrf_exempt
def search_product(request):
    req_dict = json.loads(request.body)
    key_word = req_dict['keyword']
    try:
        username = req_dict['username']
        tku = TkUser.objects.get(user__username=username)
        text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
    %s""" % iri_to_uri(tku.get_search_url(key_word))
        rst_dict = {
            'ret_code': 1,
            'reaction_list': [
                {'type': 'text', 'content': text},
            ]
        }

    except:
        text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
    %s""" % iri_to_uri('http://s-prod-04.qunzhu666.com/hpt/index.php?action=search&q=' + key_word)
        rst_dict = {
            'ret_code': 1,
            'reaction_list': [
                {'type': 'text', 'content': text},
            ]
        }

    return HttpResponse(json.dumps(rst_dict))


@csrf_exempt
def search_product_pad(request):
    try:
        username = request.GET.get('username', '')
        uin = request.GET.get('uin', '')
        key_word = request.GET.get('keyword', '')
        gid = request.GET.get('gid', '')

        if username == '' or key_word == '' or gid == '' or uin == '':
            return HttpResponse("incorrect params,username:{0},keyword:{1}, gid:{2}"
                                .format(username, key_word, gid))

        r = requests.get("http://" + S_PROD_07_INT + "/api/tk/check-search?username={0}".format(username), timeout=10)
        if r.status_code != 200:
            return HttpResponse("remote server ret_code:{0} --{1}".format(r.status_code, r.text))
        ret_code = json.loads(json.loads(r.text))

        if ret_code['data'] != 1:
            return HttpResponse("check search fail:{0}".format(ret_code['data']))

        tku = TkUser.objects.get(user__username=username)
        text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
        {}""".format(iri_to_uri(tku.get_search_url(key_word)))

        params_dict = {
            "uin": uin,
            "group_id": gid,
            "text": text,
            "type": "text"
        }
        bot_request = requests.get("http://" + S_PROD_04_INT + ":5000/send_msg_type", params=params_dict, timeout=10)
        # print bot_request.url
        if bot_request.status_code != 200:
            return HttpResponse("error ret status:{0} from remote bot server--{1}"
                                .format(bot_request.status_code, bot_request.text))
        else:
            return HttpResponse("success")

    except Exception as e:
        return HttpResponse("exception occurred:{0}".format(e.message))
    # req_dict = json.loads(request.body)
    # key_word = req_dict['keyword']
    # try:
    #     username = req_dict['username']
    #     tku = TkUser.objects.get(user__username=username)
    #     text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
    # %s""" % iri_to_uri(tku.get_search_url(key_word))
    #     rst_dict = {
    #         'ret_code': 1,
    #         'reaction_list': [
    #             {'type': 'text', 'content': text},
    #         ]
    #     }
    #
    # except:
    #     text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
    # %s""" % iri_to_uri('http://s-prod-04.qunzhu666.com/hpt/index.php?action=search&q=' + key_word)
    #     rst_dict = {
    #         'ret_code': 1,
    #         'reaction_list': [
    #             {'type': 'text', 'content': text},
    #         ]
    #     }
    #
    # return HttpResponse(json.dumps(rst_dict))


def hijack_ll(request):
    keyword = request.GET.get('keyword')
    pid = request.GET.get('pid')
    resp = requests.get(
        url=iri_to_uri('http://chong2.xiaoshijie.com/saber/index/search?search=' + keyword)
    )
    content = resp.content.decode('utf-8')
    content = content.replace('mm_122190119_25238069_95116426', pid)
    return HttpResponse(content, content_type='charset=utf-8')
