# coding=utf-8
import requests
from datetime import datetime, timedelta
import logging
import time
import os
import sys

sys.path.append('/home/new_taobaoke/taobaoke/')
# sys.path.append('/home/smartkeyerror/PycharmProjects/new_taobaoke/taobaoke')

import django

os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from broadcast.models.chatroom_models import ChatRoomQrcode

from fuli.oss_utils import beary_chat
logger = logging.getLogger('utils')

get_date_url = 'http://s-prod-04.qunzhu666.com:10024/api/robot/get_chatroom_qrcode/'
# get_date_url = 'http://s-prod-04.qunzhu666.com:10024/api/robot/get_chatroom_qrcode/'

postdate = {
    "wx_id": "wxid_3drnq3ee20fg22",
    "chatroom_id": "7218909824@chatroom"
}

if __name__ == '__main__':
    last_update_time = None
    update_time = None
    while True:
        try:
            res = requests.post(get_date_url, json=postdate)
            if res.status_code == 200:
                return_data = res.json()
                print return_data
                if return_data['ret'] == 1:
                    chatroom_id = '7218909824@chatroom'
                    name = return_data['chatroom_name']
                    url = return_data['qrcode_url']
                    create_time = datetime.now()

                    chatroom_dict = {'chatroom_id': chatroom_id, 'name': name, 'qrcode_url': url,
                                     'create_time': create_time}
                    ChatRoomQrcode.objects.update_or_create(chatroom_id=chatroom_id, defaults=chatroom_dict)

                    last_update_time = datetime.now()
                    update_time = last_update_time + timedelta(days=2)

                    logger.info('last_update_time:' + str(last_update_time))
                    logger.info('update_time:' + str(update_time))
                    while True:
                        time.sleep(3600)
                        if datetime.now().day == update_time.day:
                            while datetime.now().hour < 9 or datetime.now().hour > 21:
                                time.sleep(3600)
                            break
                else:
                    logger.error("刷新二维码请求返回异常，请求参数可能错误, 机器人小小未登录，请检查～")
                    beary_chat("刷新二维码请求返回异常，请求参数可能错误，机器人小小未登录请检查～")
                    time.sleep(7200)
            else:
                logger.info("刷新二维码请求返回失败，机器人可能未上线,等待下一次请求中～")
                time.sleep(7200)
        except Exception as e:
            logging.error(e)
            beary_chat(e)
            print(e)
            time.sleep(3600)
