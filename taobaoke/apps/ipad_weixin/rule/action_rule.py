# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from django.utils.encoding import iri_to_uri

from ipad_weixin.models import Qrcode, ChatRoom
from broadcast.models.user_models import Adzone
import urllib
import requests
import json

import logging
logger = logging.getLogger('weixin_bot')



def filter_keyword_rule(wx_id, msg_dict):
    keyword = find_buy_start(msg_dict['Content'])
    if keyword and keyword is not '':
        # 群是淘宝客群，找XX才生效
        gid = ''
        # 情况分类1 机器人自己说找XX
        if msg_dict['FromUserName'] == wx_id and "@chatroom" in msg_dict['ToUserName']:
            gid = msg_dict['ToUserName']
        # 情况分类2 群成员说找XX
        elif "@chatroom" in msg_dict['FromUserName'] and msg_dict['ToUserName'] == wx_id:
            gid = msg_dict['FromUserName']

        chatroom = ChatRoom.objects.filter(nickname__contains=u"福利社",username=gid).first()
        if chatroom:
            """
            为啥Qrcode.objects.filter(username=wx_id, md_username__isnull=False).first()
            会返回一个ms_username=''的结果 = =
            """
            qrcode_dbs = Qrcode.objects.filter(username=wx_id)
            for qrcode_db in qrcode_dbs:
                if qrcode_db.md_username != '' and qrcode_db.md_username != None:
                    md_username = qrcode_db.md_username
                    break

            adzone_db = Adzone.objects.filter(tkuser__user__username=md_username).first()
            pid = adzone_db.pid
            url_keyword = urllib.quote(keyword.encode('utf-8'))

            template_url = 'http://dianjin364.123nlw.com/saber/index/search?pid={0}&search={1}'.format(pid, url_keyword)
            judge_url = 'http://dianjin364.123nlw.com/a_api/index/search?wp=&sort=3&pid={0}&search={1}&_path=9001.SE.0'.format(pid, url_keyword)
            judge_response = requests.get(judge_url)
            judge_dict = json.loads(judge_response.content)

            from ipad_weixin.send_msg_type import send_msg_type

            if judge_dict['result']['items'] == []:
                text = u"很抱歉，您需要的{}没有找到，您可以搜索一下其他商品哦～[太阳][太阳]".format(keyword)
            else:
                text = u"""搜索商品 {0} 成功！点击下面链接查看我们给您找到的专属优惠券。
                {1}""".format(keyword, iri_to_uri(template_url))

                shop_url = judge_dict['result']['items'][0]['coverImage']
                img_msg_dict = {
                    "uin": wx_id,
                    "group_id": gid,
                    "text": shop_url,
                    "type": "img"
                }

                send_msg_type(img_msg_dict)
                logger.info('找到商品， 向 %s 推送图片' % gid)

            params_dict = {
                        "uin": wx_id,
                        "group_id": gid,
                        "text": text,
                        "type": "text"
                    }

            send_msg_type(params_dict)
            logger.info("Push text %s to group %s." % (text, gid))



def find_buy_start(s):
    # 一个中文字符等于三个字节 允许有十个字符
    if len(s) < 40:
        lst = s.split("找")
        if len(lst) > 1:
            return lst[1]
        lst = s.split("买")
        if len(lst) > 1:
            return lst[1]
    return False


if __name__ == "__main__":
    msg_dict = {u'Status': 3,
                u'PushContent': u'\u964c : 找跳绳',
                u'FromUserName': u'6610815091@chatroom',
                u'MsgId': 1650542751,
                u'ImgStatus': 1,
                u'ToUserName': u'wxid_cegmcl4xhn5w22',
                u'MsgSource': u'<msgsource>\n\t<silence>0</silence>\n\t<membercount>5</membercount>\n</msgsource>\n',
                u'Content': u'wxid_9zoigugzqipj21:\n\u627e\u62d6\u978b',
                u'MsgType': 1, u'ImgBuf': None,
                u'NewMsgId': 1469484974773846106,
                u'CreateTime': 1506652565
                }
    wx_id = 'wxid_cegmcl4xhn5w22'
    filter_keyword_rule(wx_id, msg_dict)



    """
    请求 
    http://dianjin364.123nlw.com/a_api/index/search?wp=&sort=6&pid=mm_122190119_26062749_103284242&search=%E7%BA%BD%E6%9B%BC%E7%82%B9%E8%AF%BB%E7%AC%94&_path=9001.SE.0
    没有搜索到商品的结果：
    {
        "status":{"code":1001,"msg":"ok"},
        "result":{
            "search":"\u7ebd\u66fc\u70b9\u8bfb\u7b14",
            "items":[],
            "wp":"eyJwYWdlIjoyLCJzb3J0IjoiNiIsImNpZCI6bnVsbCwic2VhcmNoIjoiXHU3ZWJkXHU2NmZjXHU3MGI5XHU4YmZiXHU3YjE0IiwidHlwZSI6bnVsbCwic2VhcmNoUGFnZSI6Mn0=",
            "isEnd":1,"type":null,
            "title":"\u7ebd\u66fc\u70b9\u8bfb\u7b14-\u963f\u56fd\u798f\u5229\u793e",
            "pid":"mm_122190119_26062749_103284242"
            }
    }
    
    有商品返回的结果：
    {
    "status":{
        "code":1001,
        "msg":"ok"
    },
    "result":{
        "search":"飞机",
        "items":[
            {
                "id":"4470149",
                "title":"超级飞机耐摔玩具小黄人飞机感应悬浮飞行器遥控飞机儿童玩具礼物",
                "itemId":"545806621017",
                "isBaoyou":false,
                "baoyouImg":"",
                "tabs":[

                ],
                "price":"¥33.9",
                "originPrice":"¥113.9",
                "amount":80,
                "totalCount":200000,
                "surplus":184082,
                "percentage":7,
                "coverImage":"http://oss3.lanlanlife.com/ce4006737a6e96a05da5c4edbbf4e48e_800x800.jpg@!1-300-90-jpg",
                "link":"/saber/detail?activityId=5b6d98a49e524a8db15f8d75a2062adb&itemId=545806621017&pid=mm_122190119_26062749_103284242&forCms=1&_path=9001.CA.0.i.545806621017",
                "monthSales":640,
                "activityId":"5b6d98a49e524a8db15f8d75a2062adb",
                "score":0,
                "priorityRecommend":""
            },
            
            
        ],
        "wp":"eyJwYWdlIjoyLCJzb3J0IjoiNiIsImNpZCI6bnVsbCwic2VhcmNoIjoiXHU5OGRlXHU2NzNhIiwidHlwZSI6bnVsbCwic2VhcmNoUGFnZSI6MX0=",
        "isEnd":0,
        "type":null,
        "title":"飞机-阿国福利社",
        "pid":"mm_122190119_26062749_103284242"
    }
}    
    """
