# -*- coding: utf-8 -*-
import datetime
import requests
from fuli.oss_utils import beary_chat


def fetch_excel(cookie_str, url):
    resp = requests.get(
        url=url,
        headers={'Cookie': cookie_str}
    )

    # 将结果写入
    f = open("scripts/alimama/pub_alimama_settle_excel.xls", "wb")
    for chunk in resp.iter_content(chunk_size=512):
        if chunk:
            f.write(chunk)
    if 'html' in resp.text:
        # 说明cookie失效
        return False
    return True
