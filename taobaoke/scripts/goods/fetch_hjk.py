# coding: utf-8
import sys
sys.path.append('/home/new_taobaoke/taobaoke')
import os
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
import django
django.setup()
import json
import requests
from datetime import datetime
import time

from broadcast.models.entry_models import JDProduct
from django.db import connection
import logging
logger = logging.getLogger('fetch_hjk')
from fuli.top_settings import  hjk_apikey

goodslist_url = 'http://www.haojingke.com/index.php/api/index/myapi?type=goodslist&apikey={apikey}&page={page}&pageSize=50'

def main(page=1, totalpage=2):
    if page <= totalpage:
        resp = requests.get(goodslist_url.format(apikey=hjk_apikey, page=page), headers={'Connection':'close'}).json()
        items = resp['data']
        for p in items:
            if float(p['wlCommissionShare'])/100  < 0.15 or \
                    not (datetime.fromtimestamp(float(p['beginTime']))
                            < datetime.now() <
                            datetime.fromtimestamp(float(p['endTime']))) :
                continue
            try:
                p_dict = {
                    'item_id' : p['skuId'],
                    'title' : p['skuName'],
                    'desc' : p['skuDesc'],
                    'item_url' : p['materiaUrl'],
                    'img_url' : p['picUrl'],
                    'price' : p['wlPrice_after'],
                    'cupon_value' : p['discount'],
                    'sold_qty' : p['sales'],
                    'commision_rate' : float(p['wlCommissionShare'])/100,
                    'commision_amount' : float(p['wlCommission']),
                    'cupon_url' : p['couponList'],
                    'cate' : p['cname']
                }
                np, created = JDProduct.objects.update_or_create(item_id=p['skuId'], defaults=p_dict)
                logger.info('JDProduct Updated.')
            except Exception, e:
                logger.error('{0} : {1}'.format(e, e.message))
            finally:
                connection.close()
        main(page+1, resp['totalpage'])


if __name__ == "__main__":
    main()
    # 每4个小时更新一次。
    time.sleep(60*60*4)