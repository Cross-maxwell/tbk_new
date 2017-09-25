# -*- coding: utf-8 -*-
import cPickle as pickle
from ipad_weixin.weixin_bot import WXBot
from ipad_weixin import weixin_bot


def send_msg_type(msg_dict):
    uin = msg_dict['uin']
    group_id = msg_dict['group_id']
    text = msg_dict['text']
    # img or text
    type = msg_dict['type']
    delay_time = msg_dict.get('delay_time', 0)


    v_user_pickle = weixin_bot.red.get('v_user_' + uin)

    v_user = pickle.loads(v_user_pickle)

    wx_bot = WXBot()
    return_msg = "1"
    if type == 'img':
        import thread
        thread.start_new_thread(wx_bot.send_img_msg, (group_id, v_user, text))
    elif type == 'text':
        text = text.encode('utf-8')
        a = text.split('《')
        taokoulin = [i for i in a if len(i) == 11]
        if len(taokoulin) > 0:
            print('taokouling is {}'.format(taokoulin[0]))
            # http://b.nqurl.com/static/tklapi/tkl.html?tkl=
            # text = text.replace('《{}《'.format(taokoulin[0]), '下单地址：http://demo.nut.la/tao/t/{}'.format(taokoulin[0]))
            text = text.replace('《{}《'.format(taokoulin[0]),
                                '下单地址： https://yiqizhuang.github.io/index.html?tkl=%EF%BF%A5{}%EF%BF%A5 '.format(
                                    taokoulin[0]))
            print(text)

        # 请求grpc 必须替换这些字符
        elif '\n' in text or '\r' in text:
            print('---include n or r---')
            #类似发单群
            text = text.replace('\r', '\\r').replace('\n', '\\n')
            text += "\\n[太阳]点击上面链接购买商品"

            import thread
            thread.start_new_thread(wx_bot.try_sleep_send, (int(delay_time), group_id, text, v_user))
        else:
            wx_bot.send_text_msg(group_id, text, v_user)
    else:
        return_msg = 'type error, should be img or text'
        print return_msg