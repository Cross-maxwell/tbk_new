import time
import requests
import json

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from broadcast.models.user_models import Adzone

def fetch_pid():
    f = open('cookie.txt')
    cookie_str = f.read()
    f.close()

    url_page = 'http://pub.alimama.com/common/adzone/adzoneManage.json?spm=a219t.7900221%2F1.1998910419.dbb742793' \
               '.DG8wds&tab=3&toPage={page}&perPageSize=40&gcid=8&t=1496324815809&pvid=60_61.141.65' \
               '.147_353_1496324813487&_tb_token_=w6HS1oAyncbq&_input_charset=utf-8'
    i = 0
    while True:
        i += 1
        resp = requests.get(
            url=url_page.format(page=i),
            headers={'Cookie': cookie_str.strip()}
        )
        # print (resp.json())
        data = resp.json()['data']
        for adzone in data['pagelist']:
            if 'dl-' in adzone['name']:


                req_dict = json.loads(adzone)
                pid, created = Adzone.objects.get_or_create(pid=req_dict['adzonePid'])
                pid.adzone_name = req_dict['name']
                pid.click_30d = req_dict['mixClick30day']
                pid.alipay_num_30d = req_dict['mixAlipayNum30day']
                pid.rec_30d = req_dict['rec30day']
                pid.alipay_rec_30d = req_dict['mixAlipayRec30day']
                pid.save()

                if created:
                    print "Adzone has been created"
                else:
                    pass

                print adzone['name']
        time.sleep(2)

        if data['paginator']['page'] == data['paginator']['lastPage']:
            break


if __name__ == "__main__":
    N = 0
    while True:
        print('{} time runs'.format(N))
        N = N + 1
        try:
            fetch_pid()
        except Exception, e:
            print e
        time.sleep(1*60*60)
