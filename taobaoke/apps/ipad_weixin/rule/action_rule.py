# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from django.utils.encoding import iri_to_uri

from ipad_weixin.models import Qrcode, ChatRoom
from broadcast.models.user_models import Adzone
import urllib


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
            text = u"""搜索商品成功！点击下面链接查看我们给您找到的专属优惠券。
            {}""".format(iri_to_uri(template_url))

            params_dict = {
                        "uin": wx_id,
                        "group_id": gid,
                        "text": text,
                        "type": "text"
                    }

            from ipad_weixin.send_msg_type import send_msg_type

            send_msg_type(params_dict)
            print "Push text %s to group %s." % (params_dict['text'], params_dict['group_id'])



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
