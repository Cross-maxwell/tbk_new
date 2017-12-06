# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import requests
import datetime
import random
import time
import urllib
import qrcode

from django.http import HttpResponse
from django.views.generic.base import View
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.utils.encoding import iri_to_uri

from broadcast.models.user_models import TkUser
from broadcast.models.entry_models import Product
from user_auth.models import PushTime
from broadcast.models.user_models import Adzone
from broadcast.models.entry_models import PushRecord, SearchKeywordMapping
from broadcast.utils.image_connect import generate_image, generate_qrcode

from fuli.oss_utils import beary_chat


# 本地测试
# phantomjs_path = '/home/smartkeyerror/PycharmProjects/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'

# 07服务器
# phantomjs_path = '/home/phantomjs/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'

import re
import logging
logger = logging.getLogger('django_views')


class PushProduct(View):
    def get(self, request):
        # 随机筛选商品
        # TODO: 为了解决推送记录的记录，则先筛选user，而非先筛选商品
        platform_id = 'make_money_together'

        # 本地测试
        # 获取登录了一起赚平台的所有user列表
        # url = "http://localhost:10024/robot/platform_user_list?platform_id={}".format(platform_id)
        # send_msg_url = 'http://localhost:10024/robot/send_msg/'

        url = "http://s-prod-04.qunzhu666.com:10024/api/robot/platform_user_list?platform_id={}".format(platform_id)

        # send_msg_url = 'http://127.0.0.1:10024/api/robot/send_msg/'
        send_msg_url = 'http://s-prod-04.qunzhu666.com:10024/api/robot/send_msg/'
        # url = "http://s-prod-04.qunzhu666.com:8080/robot/xxxx?platform_key={}".format(platform_id)

        response = requests.get(url)
        response_dict = json.loads(response.content)
        if response_dict["ret"] != 1:
            logger.error("筛选{}平台User为空".format(platform_id))
        login_user_list = response_dict["login_user_list"]

        """
        {
            "login_user_list":[
                    {"user": "smart", "wxuser_list": ["樂阳", "渺渺的"]}，
                    {"user": "keyerror", ......}
            ]
        }
        """
        for user_object in login_user_list:
            user = user_object["user"]

            # 找到该user所对应的pid
            try:
                tk_user = TkUser.get_user(user)
            except Exception as e:
                logger.error(e)
            try:
                pid = tk_user.adzone.pid
            except Exception as e:
                logger.error('{0} 获取Adzone.pid失败, reason: {1}'.format(user, e))

            wxuser_list = user_object["wxuser_list"]

            # 根据phone_num判定是否到达发单时间
            ret = is_push(user, platform_id)
            if ret == 0:
                for wxuser in wxuser_list:
                    logger.info("%s 未到发单时间" % wxuser)
            if ret == 1:
                for wxuser in wxuser_list:
                    logger.info("%s 开始本单发送" % wxuser)
                qs = Product.objects.filter(
                    ~Q(pushrecord__user_key__icontains=user,
                       pushrecord__create_time__gt=timezone.now() - datetime.timedelta(days=3)),
                    available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
                )

                # 用发送过的随机商品替代
                if qs.count() == 0:
                    qs = Product.objects.filter(
                        available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
                    )
                    beary_chat('点金推送商品失败：%s:%s 无可用商品' % (user, user_object["wxuser_list"]))

                for _ in range(50):
                    try:
                        r = random.randint(0, qs.count() - 1)
                        p = qs.all()[r]
                        break
                    except Exception as exc:
                        print "Get entry exception. Count=%d." % qs.count()
                        logger.error(exc)

                # text = p.get_text_msg(pid=pid)
                # img_url = p.get_img_msg()
                text = p.get_text_msg_wxapp()
                img_url = p.get_img_msg_wxapp(pid=pid)

                data = [img_url, text]

                request_data = {
                    "md_username": user,
                    "data": data
                }
                PushRecord.objects.create(entry=p, user_key=user)
                send_msg_response = requests.post(send_msg_url, data=json.dumps(request_data))

        return HttpResponse(json.dumps({"ret": 1}))


class AcceptSearchView(View):
    @csrf_exempt
    def post(self, request):
        req_dict = json.loads(request.body)
        username = req_dict["md_username"]
        at_user_nickname = req_dict["at_user_nickname"]
        keyword = req_dict["keyword"]

        adzone_db = Adzone.objects.filter(tkuser__user__username=username).first()
        pid = adzone_db.pid
        url_to_show = 'http://dianjin.dg15.cn/saber/index/search?pid={0}&search={1}'
        url_for_data = 'http://dianjin.dg15.cn/a_api/index/search?wp=&sort=3&pid={0}&search={1}&_path=9001.SE.0'
        try:
            if 'http' in keyword:
                # 直接从淘宝分享消息进行搜索
                # 从分享的消息中拿到商品链接（短链）和商品标题title
                link = re.findall('(http:[\d\w/\.]+)', keyword)[0]
                # 打开短链，从跳转后的url中获取到item_id, 用title去dianjin平台搜索，并比对搜索结果的item_id，如果一致则搜索到指定商品。如果有搜索结果，但不一致，
                # 返回搜索链接，供用户浏览类似商品。
                resp_html = requests.get(link).content
                try:
                    from broadcast.utils.entry_utils import get_item_info
                    try:
                        to_search_item_id = re.findall('[_&\?]id=(\d+)', resp_html.replace('\\u033d', '='))[0]
                    except IndexError:
                        to_search_item_id = re.findall('\/i(\d+)', resp_html)[0]
                    to_search_title = get_item_info(to_search_item_id)['title']
                    resp_dj = requests.get(url_for_data.format(pid, to_search_title))
                    resp_dict_dj = json.loads(resp_dj.content)
                    dj_products = resp_dict_dj['result']['items']
                except Exception as e:
                    logger.error(e)
                    return HttpResponse(json.dumps({"data": ["获取商品信息失败"], "ret": 0}))

                found = False
                other_found = False
                for dj_p in dj_products:
                    if dj_p['itemId'] == to_search_item_id:
                        found = True
                        cupon_url = 'https://uland.taobao.com/coupon/edetail?activityId={0}&itemId={1}&pid={2}&src=xsj_lanlan'.format(
                            dj_p['activityId'], dj_p['itemId'], pid)
                        target_url = 'http://dianjin.dg15.cn/a_api/index/detailData?itemId={0}&activityId={1}&refId=&pid={2}&_path=9001.SE.0.i.539365221844&src='.format(
                            dj_p['itemId'], dj_p['activityId'], pid
                        )
                        target_resp_dict = json.loads(requests.get(target_url).content)['result']['item']
                        p_dict = {
                            "title": target_resp_dict['title'],
                            "desc": target_resp_dict['recommend'],
                            "img_url": target_resp_dict['image'],
                            "cupon_value": float(target_resp_dict['amount'].strip(u'\u5143')),
                            "price": float(target_resp_dict['price'].strip(u'\xa5')),
                            'sold_qty': target_resp_dict['monthSales'],
                            # 因为没有这个字段，写死
                            'cupon_left': 20,
                            'cupon_url': cupon_url
                            }
                        from broadcast.models.entry_models import Product
                        target, created = Product.objects.update_or_create(item_id=dj_p['itemId'], defaults=p_dict)
                        img_url = target.get_img_msg_wxapp(pid)
                        text = '{0}，找到指定商品的优惠券，长按识别二维码领取'.format(at_user_nickname)
                        break
                    else:
                        other_found = True

                if found:
                    data = [img_url, text]
                elif (not found) and other_found:
                    text = '{0} 抱歉，没有找到指定商品，但是找到了类似的商品，长按识别二维码查看商品～'.format(at_user_nickname)

                    product_url = dj_products[0]['coverImage']

                    short_url = get_short_url(url_to_show.format(pid, to_search_title))
                    qrcode_flow = qrcode.make(short_url).convert("RGBA").tobytes("jpeg", "RGBA")
                    img_url = generate_image([product_url], qrcode_flow)

                    data = [img_url, text]
                else:
                    text = '{0}，很抱歉，您需要的商品商品没有找到哦～您可以搜索一下其他商品哦～[太阳][太阳]'.format(at_user_nickname)
                    data = [text]
                return HttpResponse(json.dumps({"data": data}))

            else:
                # 普通搜索，"找xx"、"买XX"
                template_url = url_to_show.format(pid, keyword)
                judge_url = url_for_data.format(pid, keyword)
                judge_response = requests.get(judge_url)
                judge_dict = json.loads(judge_response.content)

                if not judge_dict['result']['items']:
                    text = u"{0}，很抱歉，您需要的{1}没有找到哦～您可以搜索一下其他商品哦～[太阳][太阳]".\
                        format(at_user_nickname, keyword)
                    data = [text]
                else:

                    product_url = judge_dict['result']['items'][0]['coverImage']

                    # short_url = get_short_url(template_url)
                    # qrcode_flow = qrcode.make(short_url).convert("RGBA").tobytes("jpeg", "RGBA")
                    # img_url = generate_image([product_url], qrcode_flow)

                    # TODO: 待前端完成
                    logger.info("生成搜索小程序二维码: username: {}, keyword: {}".format(username, keyword))
                    # 将用户的username以及keyword存起来，传递给小程序一个id值即可
                    keyword_mapping_id = SearchKeywordMapping.objects.create(username=username, keyword=keyword).id
                    req_data = {
                        "page": "pages/search/search",
                        "scene": "{0}".format(keyword_mapping_id)
                    }
                    qrcode_flow = generate_qrcode(req_data)
                    img_url = generate_image([product_url], qrcode_flow)

                    random_seed = random.randint(1000, 2000)
                    text = "{0}，搜索  {1}  成功！此次共搜索到相关产品{2}件，长按识别小程序码查看为您找到的高额优惠券。\n" \
                           "================\n" \
                           "图片仅供参考，详细信息请扫描二维码查看～".format(at_user_nickname, keyword, random_seed)

                    data = [img_url, text]
                return HttpResponse(json.dumps({"data": data}))
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({"data": ['搜索失败']}))


def get_short_url(long_url):
    template_url = urllib.quote(iri_to_uri(long_url))
    short_url_respose = requests.get(
        'http://api.weibo.com/2/short_url/shorten.json?source=2849184197&url_long=' + template_url)
    short_url = short_url_respose.json()['urls'][0]['url_short']
    return short_url


class AppSearchListView(View):
    """
    接口: /product/search_list
    """
    @csrf_exempt
    def post(self, request):
        # req_dict = json.loads(request.body)
        # id = req_dict["id"]
        # page = req_dict.get("page", "1")
        # sort = req_dict.get("sort", "1")
        #
        # # 维护一个dict
        # sort_dict = {
        #     "1": "MS",
        #     "2": "Mi",
        #     "3": "My",
        #     "8": "OC",
        # }
        # sort_params = sort_dict[sort]
        #
        # keyword = req_dict.get("keyword", "")
        # keyword_mapping = SearchKeywordMapping.objects.get(id=id)
        # md_username = keyword_mapping.username
        # if not keyword:
        #     keyword = keyword_mapping.keyword
        #
        # try:
        #     tk_user = TkUser.get_user(md_username)
        #     pid = tk_user.adzone.pid
        #
        #     midlle_url = "http://dianjin.dg15.cn/a_api/index/search?wp=&sort=1&pid={pid}&search={keyword}&_path=9001.SE.0". \
        #         format(pid=pid, keyword=keyword)
        #     midlle_response = requests.get(midlle_url)
        #     wp = json.loads(midlle_response.content)["result"]["wp"]
        #     wp_list = list(wp)
        #
        #     if page == "1":
        #         search_url = "http://dianjin.dg15.cn/a_api/index/search?wp=&sort={sort}&pid={pid}&search={keyword}&_path=9001.SE.0".format(
        #             sort=sort, pid=pid, keyword=keyword
        #         )
        #         response = requests.get(search_url)
        #         return HttpResponse(response.content)
        #
        #     # 替换页码
        #     if page == "2":
        #         wp_list[11] = "y"
        #     if page == "3":
        #         wp_list[11] = "z"
        #     if int(page) >= 4:
        #         wp_list[11] = str(int(page) - 4)
        #
        #     # 替换排序方式
        #     wp1 = ''.join(wp_list)
        #     wp_list1 = list(wp1)
        #     wp_list1[24:26] = list(sort_params)
        #     final_wp = ''.join(wp_list1)
        #
        #     # TODO： 这里wp的值可能会发生改变
        #     search_url = "http://dianjin.dg15.cn/a_api/index/search?wp={wp}&sort={sort}&pid={pid}&search={keyword}&_path=9001.SE.0".format(
        #         wp=final_wp, sort=sort, pid=pid, keyword=keyword
        #     )
        #     response = requests.get(search_url)
        #     return HttpResponse(response.content)
        # except Exception as e:
        #     logger.error(e)

        # TODO: 待前端完成
        req_dict = json.loads(request.body)
        # TODO: 接受小程序传来的id值，去数据库中拿出相应数据
        id = req_dict["id"]
        sort = req_dict.get("sort", "1")
        wp = req_dict.get("wp", "")

        keyword = req_dict.get("keyword", "")
        keyword_mapping = SearchKeywordMapping.objects.get(id=id)
        md_username = keyword_mapping.username
        if not keyword:
            keyword = keyword_mapping.keyword
        try:
            tk_user = TkUser.get_user(md_username)
            pid = tk_user.adzone.pid

            if not wp:
                search_url = "http://dianjin.dg15.cn/a_api/index/search?wp=&sort={sort}&pid={pid}&search={keyword}&_path=9001.SE.0".format(
                    sort=sort, pid=pid, keyword=keyword
                )
            else:
                search_url = "http://dianjin.dg15.cn/a_api/index/search?wp={wp}&sort={sort}&pid={pid}&search={keyword}&_path=9001.SE.0".format(
                    wp=wp, sort=sort, pid=pid, keyword=keyword
                )
            response = requests.get(search_url)
            return HttpResponse(response.content)
        except Exception as e:
            logger.error(e)


class AppSearchDetailView(View):
    """
    接受itemId, md_username, activityId, 返回商品详情以及淘口令
    接口： /product/search_detail
    """
    @csrf_exempt
    def post(self, request):
        req_dict = json.loads(request.body)
        itemId = req_dict["itemId"]
        activityId = req_dict["activityId"]
        # TODO: 接受小程序传来的id值，去数据库中拿出相应数据
        id = req_dict["id"]
        keyword_mapping = SearchKeywordMapping.objects.get(id=id)
        md_username = keyword_mapping.username

        try:
            tk_user = TkUser.get_user(md_username)
            pid = tk_user.adzone.pid

            detail_url = "http://dianjin.dg15.cn/a_api/index/detailData?itemId={itemId}&activityId={activityId}&refId=&pid={pid}" \
                         "&_path=9001.SE.0.i.{path}&src=".format(
                itemId=itemId, activityId=activityId, pid=pid, path=itemId
            )
            response = requests.get(detail_url)
            detail_dict = json.loads(response.content)
            item = detail_dict["result"]["item"]

            # 根据itemId等生成tkl
            tkl_url = "http://dianjin.dg15.cn/a_api/index/getTpwd"

            # 共需要6个字段
            data = {
                "itemId": itemId,
                "activityId": activityId,
                "pid": pid,
                "image": item["image"],
                "title": item["title"],
                "sellerId": detail_dict["result"]["item"]["shop"]["sellerId"]

            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            tkl_response = requests.post(tkl_url, data=data, headers=headers)
            res_dict = json.loads(tkl_response.content)
            tkl = res_dict["status"]["msg"]
            detail_dict["tkl"] = tkl
            response_data = json.dumps(detail_dict)
            print response_data
            return HttpResponse(response_data)
        except Exception as e:
            logger.info("itemId: {}, 商品已失效".format(itemId))
            return HttpResponse(json.dumps({"ret": 0, "reason": "商品失效了哦～"}))


def is_push(md_username, wx_id):
    """
    md_username
    wx_id
    """
    try:
        pushtime = PushTime()
        user_pt = pushtime.get_pushtime(md_username)
        push_interval = user_pt.interval_time

        cache_key = md_username + '_' + wx_id + '_last_push'
        cache_time_format = "%Y-%m-%d %H:%M:%S"

        cur_time = datetime.datetime.now()
        # 上一次推送的时间
        last_push_time = cache.get(cache_key)
        if last_push_time is None:
            is_within_interval = True
        else:
            dt_last_push_time = datetime.datetime.strptime(last_push_time, cache_time_format)
            is_within_interval = dt_last_push_time + datetime.timedelta(minutes=int(push_interval)) <= cur_time

        dt_begin_pt = datetime.datetime.strptime(user_pt.begin_time.replace('24:00', '23:59'), '%H:%M')
        dt_end_pt = datetime.datetime.strptime(user_pt.end_time.replace('24:00', '23:59'), '%H:%M')

        if dt_begin_pt.time() < cur_time.time() < dt_end_pt.time() and is_within_interval:
            ret_code = 1
            cache.set(cache_key, datetime.datetime.strftime(cur_time, cache_time_format), 3600 * 10)
        else:
            ret_code = 0

        return ret_code
    except Exception as e:
        logger.error(e)


class AppProductJsonView(View):
    def get(self, request):
        # 返回商品的类别，
        pass


class ProductDetail(View):
    """
    给小程序用的商品详情请求接口
    """
    def get(self, request):
        id = request.GET.get('id')
        if id is None:
            return HttpResponse(json.dumps({'data': 'losing param \'id\'.'}), status=400)
        try:
            p = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return HttpResponse(json.dumps({'data': 'Bad param \'id\' or product does not exist'}), status=400)
        p_detail = p.productdetail
        activity_id = re.findall('activityId=([\w\d]+)',p.cupon_url)[0]
        try:
            detail_url = "http://dianjin.dg15.cn/a_api/index/detailData?itemId={itemId}&activityId={activityId}&refId=&pid=" \
                         "&_path=9001.SE.0.i.{path}&src=".format(
                itemId=p.item_id, activityId=activity_id, path=p.item_id
            )
            response = requests.get(detail_url)
            detail_dict = json.loads(response.content)
            item = detail_dict["result"]["item"]
        except Exception, e:
            p.available = False
            p.save()
            logger.info("itemId: {}, 商品已失效".format(p.item_id))
            return HttpResponse(json.dumps({"ret": 0, "reason": "商品失效了哦～"}))
        resp_dict = {
            'title': p.title,
            'desc': p.desc,
            'img': p.img_url,
            'cupon_value': p.cupon_value,
            'price': p.price,
            'org_price': p.org_price,
            'provcity': p_detail.provcity,
            'seller_nick': p_detail.seller_nick,
            'small_imgs': json.loads(p_detail.small_imgs),
            'detailImages': item['detailImages'],
            'recommend': item['recommend'],
            # 最根类
            'root_cat': p_detail.cate.root_cat_name,
            # 类别
            'cat': p_detail.cate.cat_name,
            # 子类别
            'cat_leaf': p_detail.cate.cat_leaf_name
        }
        return HttpResponse(json.dumps({'data': resp_dict}), status=200)


class SendArtificialMsg(View):
    """
    接口：  /tk/send_artifical_msg/
    """
    @csrf_exempt
    def post(self, request):
        req_dict = json.loads(request.body)
        product_id = req_dict["item_id"]
        artifical_data = req_dict["data"]
        # 首先根据product_id拿到商品，循环遍历已登录user，获取pid并替换
        product = Product.objects.get(item_id=product_id)
        available = product.available
        if not available:
            return HttpResponse(json.dumps({"ret": 0, "reason": "商品已失效"}))

        platform_id = 'make_money_together'

        url = "http://s-prod-04.qunzhu666.com:10024/api/robot/platform_user_list?platform_id={}".format(platform_id)

        localhost_send_msg_url = 'http://localhost:10024/api/robot/send_msg/'
        send_msg_url = 'http://s-prod-04.qunzhu666.com:10024/api/robot/send_msg/'

        response = requests.get(url)
        response_dict = json.loads(response.content)
        if response_dict["ret"] != 1:
            logger.error("筛选{}平台User为空".format(platform_id))
        login_user_list = response_dict["login_user_list"]

        """
        {
            "login_user_list":[
                    {"user": "smart", "wxuser_list": ["樂阳", "渺渺的"]}，
                    {"user": "keyerror", ......}
            ]
        }
        """
        text = product.get_text_msg_wxapp()

        for user_object in login_user_list:
            # TODO: 压力过大，主要压力来自于requests库长连接数量的限制，此处需要注意
            data = []
            user = user_object["user"]

            # 找到该user所对应的pid
            try:
                tk_user = TkUser.get_user(user)
            except Exception as e:
                logger.error(e)
            try:
                pid = tk_user.adzone.pid
            except Exception as e:
                logger.error('{0} 获取Adzone.pid失败, reason: {1}'.format(user, e))

            try:
                img_url = product.get_img_msg_wxapp(pid=pid)

                data.append(img_url)
                data.append(text)
                for item in artifical_data:
                    data.append(item)

                # 这里不能用TCP长连接
                headers = {
                    "Connection": "close"
                }

                request_data = {
                    "md_username": user,
                    "data": data
                }
                send_msg_response = requests.post(send_msg_url, data=json.dumps(request_data), headers=headers)

                logger.info("SendArtificialMsg response: {}".format(send_msg_response.content))

                artifical_data = req_dict["data"]
                time.sleep(3.5)
            except Exception as e:
                logger.error(e)

        return HttpResponse(json.dumps({"ret": 1}))




# class SendSignNotice(View):
#     """
#     接口： http://s-prod-04.qunzhu666.com/tk/send_signin_notice
#     """
#     def get(self, request):
#         wxuser_list = WxUser.objects.filter(login__gt=0, is_customer_server=False).all()
#         for wx_user in wxuser_list:
#             chatroom_list = ChatRoom.objects.filter(wx_user__username=wx_user.username,
#                                                     nickname__icontains=u"福利社").all()
#             for chatroom in chatroom_list:
#                 import thread
#                 thread.start_new_thread(self.send_nitice, (wx_user, chatroom))
#         return HttpResponse(json.dumps({"ret": 1}))
#
#     def send_nitice(self, wx_user, chatroom):
#         text_msg_dict = {
#             # 群主 id
#             "uin": wx_user.username,
#             # 群/联系人 id
#             "group_id": chatroom.username,
#             "text": "签到开始了，回复 {0} 就可以签到哦～".format("你想要的这里都有"),
#             "type": "text",
#             "delay_time": 40
#         }
#
#         img_msg_dict = {
#             "uin": wx_user.username,
#             "group_id": chatroom.username,
#             "text": "http://ww4.sinaimg.cn/large/0060lm7Tly1fkt5khyyygj30hs0s074z.jpg",
#             "type": "img"
#         }
#
#         from ipad_weixin.send_msg_type import send_msg_type
#         send_msg_type(img_msg_dict, at_user_id='')
#         send_msg_type(text_msg_dict, at_user_id='')

















