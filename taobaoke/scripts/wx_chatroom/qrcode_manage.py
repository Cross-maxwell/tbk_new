import requests
from datetime import datetime, timedelta
import logging
import time
import os
import sys

sys.path.append('/home/new_taobaoke/taobaoke/')

import django

os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from broadcast.models.chatroom_models import ChatRoomQrcode

logger = logging.getLogger('utils')

get_date_url = 'http://s-prod-04.qunzhu666.com:10024/api/robot/get_chatroom_qrcode/'

postdate = {
    "wx_id": "wxid_3drnq3ee20fg22",
    "chatroom_id": "7218909824@chatroom"
}

if __name__ == '__main__':
    while True:
        last_update_time = None
        update_time = None
        try:
            res = requests.post(get_date_url, json=postdate)
            return_data = res.json()
            print return_data

            chatroom_id = '7218909824@chatroom'
            name = return_data['chatroom_name']
            url = return_data['qrcode_url']
            create_time = datetime.now()

            chatroom_dict = {'chatroom_id': chatroom_id, 'name': name, 'qrcode_url': url,
                             'create_time': create_time}
            ChatRoomQrcode.objects.update_or_create(chatroom_id=chatroom_id, defaults=chatroom_dict)

            logger.info('response_state:' + str(res.status_code))

            last_update_time = datetime.now()
            update_time = last_update_time + timedelta(days=4)

            logger.info('last_update_time:' + str(last_update_time))
            logger.info('update_time:' + str(update_time))

            while True:
                time.sleep(3600)
                if datetime.now().day == update_time.day:
                    break
        except Exception as e:
            logging.error(e)
            print(e)
