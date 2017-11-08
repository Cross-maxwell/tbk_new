# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from ipad_weixin.models import ChatRoom, SignInRule, ChatroomMember
import time
import re
from ipad_weixin.send_msg_type import send_msg_type
import requests
import json
import logging
logger = logging.getLogger('weixin_bot')


def filter_sign_in_keyword(nickname, wx_id, msg_dict):
    """
    # 机器人自己在群里说话
    {u'Status': 3,
    u'PushContent': u'',
    u'FromUserName': u'wxid_cegmcl4xhn5w22',
    u'MsgId': 1650554654,
    u'ImgStatus': 1,
    u'ToUserName': u'6947816994@chatroom',
    u'MsgSource': u'',
    u'Content': u'\u4f60\u60f3\u8981\u7684\u90fd\u5728\u8fd9\u91cc',
    u'MsgType': 1,
    u'ImgBuf': None,
    u'NewMsgId': 1582711830148784131,
    u'CreateTime': 1508809888}
    """
    # 首先判断content中是否包含红包口令
    if ':' in msg_dict['Content']:
        content = msg_dict['Content'].split(':')[1].strip()
    else:
        content = msg_dict['Content']

    signin_db = SignInRule.objects.all()
    keywords = [signin.keyword for signin in signin_db]

    speaker_id = ''
    chatroom = ''
    from_user_id = ''
    if content in keywords:
        logger.info("%s: 进入签到" % nickname)
        singin_rule = SignInRule.objects.filter(keyword=content).first()
        # 机器人自己在群里说话
        if '@chatroom' in msg_dict['ToUserName']:
            speaker_id = msg_dict['FromUserName']  # 微信ID
            from_user_id = msg_dict['ToUserName']  # 群ID
            chatroom = ChatRoom.objects.get(username=msg_dict['ToUserName'])
        # 群成员签到
        if '@chatroom' in msg_dict['FromUserName']:
            chatroom = ChatRoom.objects.get(username=msg_dict['FromUserName'])
            speaker_id = msg_dict['Content'].split(':')[0]
            from_user_id = msg_dict['FromUserName']

        speaker = ChatroomMember.objects.filter(username=speaker_id).first()
        speaker_name = speaker.nickname
        if u"福利社" in chatroom.nickname:
            data = {
                "speaker_nick_name_trim": get_nick_name_trim(speaker_name),
                "time": {"$date": int(round(time.time() * 1000))},
                "speaker_head_img_url": speaker.small_head_img_url,
                "speaker_nick_name_emoji_unicode": get_nick_name_emoji_unicode(speaker_name),
                "from_user_id": from_user_id,
                "speaker_id": speaker_id
            }

            url = 'http://s-poc-02.qunzhu666.com/365/api/clockin/'
            request_url = url + singin_rule.red_packet_id
            json_data = json.dumps(data)
            response = requests.post(request_url, data=json_data)
            body = json.loads(response.content)

            reaction_list = body['reaction_list']
            for reaction in reaction_list:
                if reaction['type'] == 'text':
                    text = reaction['content']

                    text_msg_dict = {
                        "uin": wx_id,
                        "group_id": from_user_id,
                        "text": "@" + speaker_name + '\\n' + text,
                        "type": "text",
                    }
                    send_msg_type(text_msg_dict, at_user_id=speaker_id)
                    logger.info("%s: 签到发送文字" % nickname)

                elif reaction['type'] == 'img':

                    img_url = reaction['content']
                    if img_url:
                        img_msg_dict = {
                            "uin": wx_id,
                            "group_id": from_user_id,
                            "text": img_url,
                            "type": "img"
                        }
                        send_msg_type(img_msg_dict, at_user_id=None)
                    logger.info("%s: 签到发送图片" % nickname)
    else:
        pass


def get_nick_name_emoji_unicode(nick_name):
    return convert_emoji_from_html_to_unicode(nick_name)

def get_nick_name_trim(nick_name):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u'\u2600-\u26FF\u2700-\u27BF'
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', get_nick_name_emoji_unicode(nick_name))


def convert_emoji_from_html_to_unicode(s):
    """
    将网页的emoji编码转化为unicode
    """
    pattern = '<span class="emoji emoji(.{4,5})"></span>'
    rst = re.search(pattern, s)
    if rst is None:  # No emoji found.
        return s
    emoji_id = rst.group(1)
    emoji_unicode = ('\U' + '0' * (8 - len(emoji_id)) + emoji_id).decode('raw-unicode-escape')
    return re.sub(pattern, emoji_unicode, s)

if __name__ == '__main__':
    wx_id = "wxid_cegmcl4xhn5w22"
    msg_dict = {u'Status': 3,
                u'PushContent': u'\u964c : \u4eca\u5929\u6211\u8981\u597d\u597d\u8d5a\u94b1',
                u'FromUserName': u'6947816994@chatroom',
                u'MsgId': 1650548075,
                u'ImgStatus': 1,
                u'ToUserName': u'wxid_cegmcl4xhn5w22',
                u'MsgSource': u'<msgsource>\n\t<silence>0</silence>\n\t<membercount>4</membercount>\n</msgsource>\n',
                u'Content': u'wxid_9zoigugzqipj21:\n\u4eca\u5929\u6211\u8981\u597d\u597d\u8d5a\u94b1',
                u'MsgType': 1,
                u'ImgBuf': None,
                u'NewMsgId': 9134144839524001013,
                u'CreateTime': 1507951268
    }

    filter_sign_in_keyword(wx_id, msg_dict)
