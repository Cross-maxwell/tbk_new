# coding: utf-8
import os
import sys
rpath = os.path.abspath('../..')
sys.path.append('rpath')
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()
import top.api
from fuli.top_settings import lanlan_apikey
import requests
import thread
import logging
logger = logging.getLogger('fetch_lanlan')


def update_cate(ps, i):
    logger.info('Thread-{}  start.'.format(i))
    for p in ps:
        if p.cate is None:
            resp = requests.get('http://www.lanlanlife.com/product/itemInfo?apiKey={0}&itemId={1}'.format(lanlan_apikey, p.item_id)).json()
            if resp['status']['code'] == 1001 and resp['result']:
                p.cate = resp['result']['category']
                p.save()
                logger.info('ok')
            else: continue
    logger.info('Thread-{}  done.'.format(i))


if __name__=="__main__":
    from broadcast.models.entry_models import Product
    ps = Product.objects.all()
    n = ps.count() // 5000
    for i in range(n+1):
        sub_ps = ps[i*5000 : i*5000 + 5000]
        thread.start_new_thread(update_cate, (sub_ps,i))
