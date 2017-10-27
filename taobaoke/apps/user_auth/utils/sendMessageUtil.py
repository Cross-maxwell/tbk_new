# -*- coding: utf-8 -*-
import requests
import json
from user_auth import settings


def send_message(phoneNum, message):
    return_value = False
    resp = requests.post("http://sms-api.luosimao.com/v1/send.json",
                         auth=("api", settings.luosimao_kye),
                         data={
                             "mobile": phoneNum,
                             "message": message
                         }, timeout=3, verify=False)
    result = json.loads(resp.content)
    if result['error'] == 0:
        return_value = True
    return return_value