# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from ipad_weixin.models import ChatRoom, WxUser, SignInRule, ChatroomMember
import time
import re
from ipad_weixin.send_msg_type import send_msg_type
import requests
import json


def filter_sign_in_keyword(wx_id, msg_dict):
    # wx_id 机器人id
    """
    群成员msg_dict
    {u'Status': 3, u'PushContent': u'\u964c : \u4eca\u5929\u6211\u8981\u597d\u597d\u8d5a\u94b1\uff01',
    u'FromUserName': u'6610815091@chatroom', u'MsgId': 1650546494, u'ImgStatus': 1, u'ToUserName': u'wxid_cegmcl4xhn5w22', u'MsgSource': u'<msgsource>\n\t<silence>0</silence>\n\t<membercount>8</membercount>\n</msgsource>\n', u'Content': u'wxid_9zoigugzqipj21:\n\u4eca\u5929\u6211\u8981\u597d\u597d\u8d5a\u94b1\uff01', u'MsgType': 1,
    u'ImgBuf': None, u'NewMsgId': 8821568761386270169, u'CreateTime': 1507696130}

    群主msg_dict
    {u'Status': 3, u'PushContent': u'', u'FromUserName': u'wxid_cegmcl4xhn5w22',
    u'MsgId': 1650545455, u'ImgStatus': 1, u'ToUserName': u'6610815091@chatroom',
    u'MsgSource': u'', u'Content': u'\u4eca\u5929\u6211\u8981\u597d\u597d\u8d5a\u94b1',
    u'MsgType': 1, u'ImgBuf': None, u'NewMsgId': 6845796722624900838, u'CreateTime': 1507619652}
    :param wx_id:
    :param msg_dict:
    :return:
    """
    if '@chatroom' not in msg_dict['FromUserName']:
        return

    content = msg_dict['Content'].split(':')[1].strip()
    # keyword_db数据库中取出群所对应的红包id
    signin_db = SignInRule.objects.all()
    keywords = [signin.keyword for signin in signin_db]
    if content in keywords:
        speaker_id = msg_dict['Content'].split(':')[0]
        # speaker_name = msg_dict['PushContent'].rsplit(':',1)[0].strip()

        speaker = ChatroomMember.objects.filter(username=speaker_id).first()
        singin_rule = SignInRule.objects.filter(keyword=content).first()

        speaker_name = speaker.nickname
        speaker_nick_name_trim = get_nick_name_trim(speaker_name)
        speaker_head_img_url = speaker.small_head_img_url
        speaker_nick_name_emoji_unicode = get_nick_name_emoji_unicode(speaker_name)
        from_user_id = msg_dict['FromUserName']

        data = {
            "speaker_nick_name_trim": speaker_nick_name_trim,
            "time": {"$date": int(round(time.time()*1000))},
            "speaker_head_img_url": speaker_head_img_url,
            "speaker_nick_name_emoji_unicode": speaker_nick_name_emoji_unicode,
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
                    "text": text,
                    "type": "text",
                }
                send_msg_type(text_msg_dict)

            elif reaction['type'] == 'img':

                img_url = reaction['content']
                if img_url:
                    img_msg_dict = {
                        "uin": wx_id,
                        "group_id": from_user_id,
                        "text": img_url,
                        "type": "img"
                    }
                    send_msg_type(img_msg_dict)

        """
        
        {"code":1, "text":"扫码关注下方公众号方可签到！关注后再！到！群！里！签！一！次！如果你已经关注但未能识别，请取关后重新关注再签到一次~如果还是无效，则是您的昵称中包含特殊符号/表情无法识别，请修改微信昵称后，取关再重新关注签到。", 
        "speak":"true", "img_url":"http://pin.guofenjie.cn/img/J0EloHVeWT8Z3oPzeAKZ.jpg", "ret_code":1, 
        "reaction_list":[{"type":"text", "content":"扫码关注下方公众号方可签到！关注后再！到！群！里！签！一！次！如果你已经关注但未能识别，请取关后重新关注再签到一次~如果还是无效，则是您的昵称中包含特殊符号/表情无法识别，请修改微信昵称后，取关再重新关注签到。"}, 
        {"type":"img", "content":"http://pin.guofenjie.cn/img/J0EloHVeWT8Z3oPzeAKZ.jpg"}]}
        """


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


    """
    {u'Status': 3, 
    u'PushContent': u'\u964c : \u627e\u62d6\u978b', 
    u'FromUserName': u'6610815091@chatroom', 
    u'MsgId': 1650542751, 
    u'ImgStatus': 1, 
    u'ToUserName': u'wxid_cegmcl4xhn5w22', 
    u'MsgSource': u'<msgsource>\n\t<silence>0</silence>\n\t<membercount>5</membercount>\n</msgsource>\n', 
    u'Content': u'wxid_9zoigugzqipj21:\n\u627e\u62d6\u978b', 
    u'MsgType': 1, u'ImgBuf': None, 
    u'NewMsgId': 1469484974773846106, 
    u'CreateTime': 1506652565}
    

    {
      u'Status': 3,
      u'PushContent': u'',
      u'FromUserName': u'wxid_cegmcl4xhn5w22',
      u'MsgId': 1650548067,
      u'ImgStatus': 1,
      u'ToUserName': u'6947816994@chatroom',
      u'MsgSource': u'',
      u'Content': u'\u4eca\u5929\u6211\u8981\u597d\u597d\u8d5a\u94b1',
      u'MsgType': 1,
      u'ImgBuf': None,
      u'NewMsgId': 6299110954078902469,
      u'CreateTime': 1507950629
    }
    """