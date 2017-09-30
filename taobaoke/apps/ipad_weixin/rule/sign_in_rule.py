# coding:utf8

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()


def filter_sign_in_keyword(wx_id, msg_dict):
    # wx_id 群主id
    keyword = msg_dict['Content']
    # keyword_db数据库中取出群所对应的红包id
    """
    {u'Status': 3, u'PushContent': u'\u964c : \u627e\u62d6\u978b', 
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
        发消息成员 wx_id : msgh_dict['Content'] 谁：说了什么
        时间 msg_dict['CreateTime']
        
    该数据库应有字段：
        群名称-关键词-红包id
    """