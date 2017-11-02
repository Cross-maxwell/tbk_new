# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from django.utils.encoding import iri_to_uri

from ipad_weixin.models import Qrcode, ChatRoom, ChatroomMember, WxUser
from broadcast.models.user_models import Adzone
import urllib
import requests
import json

import logging
logger = logging.getLogger('weixin_bot')


def filter_keyword_rule(wx_id, msg_dict):
    keyword = find_buy_start(msg_dict['Content'])
    if keyword and keyword is not '':
        wx_user_list = WxUser.objects.filter(username=wx_id, is_customer_server=True)
        if wx_id in [wx_user.username for wx_user in wx_user_list]:
            return
        # 群是淘宝客群，找XX才生效
        gid = ''
        at_user_id = ''
        at_user_nickname = ''
        # 情况分类1 机器人自己说找XX
        if msg_dict['FromUserName'] == wx_id and "@chatroom" in msg_dict['ToUserName']:
            gid = msg_dict['ToUserName']
            at_user_nickname = '@' + WxUser.objects.get(username=wx_id).nickname

        # 情况分类2 群成员说找XX
        elif "@chatroom" in msg_dict['FromUserName'] and msg_dict['ToUserName'] == wx_id:
            gid = msg_dict['FromUserName']
            at_user_id = msg_dict['Content'].split(':')[0]
            at_user_db = ChatroomMember.objects.filter(username=at_user_id).first()
            at_user_nickname = '@' + at_user_db.nickname

        chatroom = ChatRoom.objects.filter(nickname__contains=u"福利社",username=gid).first()
        if chatroom:
            try:
                qrcode_db = Qrcode.objects.filter(username=wx_id, md_username__isnull=False).order_by('-id').first()
                md_username = qrcode_db.md_username

                adzone_db = Adzone.objects.filter(tkuser__user__username=md_username).first()
                pid = adzone_db.pid
                url_keyword = urllib.quote(keyword.encode('utf-8'))

                template_url = 'http://dianjin.dg15.cn/saber/index/search?pid={0}&search={1}'.format(pid, url_keyword)
                judge_url = 'http://dianjin.dg15.cn/a_api/index/search?wp=&sort=3&pid={0}&search={1}&_path=9001.SE.0'.format(pid, url_keyword)
                judge_response = requests.get(judge_url)
                judge_dict = json.loads(judge_response.content)

                # 重载template_url, 用于从微博api获取短链
                template_url = urllib.quote(iri_to_uri(template_url))
                short_url_respose = requests.get(
                    'http://api.weibo.com/2/short_url/shorten.json?source=2849184197&url_long=' + template_url)
                short_link = short_url_respose.json()['urls'][0]['url_short']


                import random
                quant=random.randint(1000, 2000)

                from ipad_weixin.send_msg_type import send_msg_type

                if judge_dict['result']['items'] == []:
                    text = u"{0}，很抱歉，您需要的{1}没有找到，您可以搜索一下其他商品哦～[太阳][太阳]".format(at_user_nickname, keyword)
                else:
                    text = "{0}，搜索  {1}  成功！此次共搜索到相关产品{2}件，点击链接查看为您找到的天猫高额优惠券。\n" \
                           "{3}\n" \
                           "「点击上面链接查看宝贝」\n" \
                           "================\n" \
                           "图片仅供参考，详细信息请点击链接～".format(at_user_nickname, keyword, quant, short_link)

                    shop_url = judge_dict['result']['items'][0]['coverImage']
                    img_msg_dict = {
                        "uin": wx_id,
                        "group_id": gid,
                        "text": shop_url,
                        "type": "img"
                    }

                    send_msg_type(img_msg_dict, at_user_id)
                    logger.info('找到商品， 向 %s 推送图片' % gid)

                params_dict = {
                            "uin": wx_id,
                            "group_id": gid,
                            "text": text,
                            "type": "text"
                        }

                send_msg_type(params_dict, at_user_id)
                logger.info("Push text %s to group %s." % (text, gid))
            except Exception as e:
                logger.error(e)


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
                u'ToUserName': u'wxid_ozdmesmnpy5g22',
                u'MsgSource': u'<msgsource>\n\t<silence>0</silence>\n\t<membercount>5</membercount>\n</msgsource>\n',
                u'Content': u'wxid_9zoigugzqipj21:\n\u627e\u62d6\u978b',
                u'MsgType': 1, u'ImgBuf': None,
                u'NewMsgId': 8330079787334973454,
                u'CreateTime': 1508208110
                }
    wx_id = 'wxid_ozdmesmnpy5g22'
    filter_keyword_rule(wx_id, msg_dict)

