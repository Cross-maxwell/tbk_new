# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from ipad_weixin.models import ChatRoom, WxUser, SignInRule, ChatroomMember
import time

def filter_sign_in_keyword(wx_id, msg_dict):
    # wx_id 机器人id
    content = msg_dict['Content']
    # keyword_db数据库中取出群所对应的红包id
    signin_db = SignInRule.objects.all()
    keywords = [signin.keyword for signin in signin_db]
    if content in keywords:
        speaker_id = msg_dict['Content'].split(':')[0]
        speaker_name = msg_dict['PushContent'].split(':')[0]
        speaker_head_img_url = ChatroomMember.objects.get(username=speaker_id)
        red_packet_id = SignInRule.objects.get(keyword=content)

        data = {
            "speaker_nick_name_trim": '',
            "time": {"$date": int(round(time.time()*1000))},
            "speaker_head_img_url": '',
            "speaker_nick_name_emoji_unicode": '',
            "from_user_id": msg_dict['FromUserName'],
            "speaker_id": msg_dict['Content'].split(':')[0]
        }












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
    
    
    
    msg_dict中包括谁在哪儿说了什么，以及说话的时间
        群名称: msg_dict['FromUserName']
        群主： msg_dict['ToUserName']
        发消息成员 wx_id : msg_dict['Content'] 谁：说了什么
        时间 msg_dict['CreateTime']
        
    该数据库应有字段：
        群名称-关键词-红包id
    """