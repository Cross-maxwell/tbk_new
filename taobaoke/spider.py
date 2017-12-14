# coding: utf-8
import requests
import lxml.html

import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
django.setup()

from mini_program.models import WishWall
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def get_source(page):
    url = "http://wish.0575life.com/index.asp?page={}".format(page)
    response = requests.get(url)
    return response.content.decode('gbk')


def main(source):
    selector = lxml.html.fromstring(source)
    wish_list = selector.xpath('//div[@class="cf"]')
    for wish in wish_list:
        content = wish.xpath('div[@class="Detail"]/span[@class="content"]/text()')
        sign = wish.xpath('div[@class="Sign"]/div[1]/text()')
        try:
            if content[0] and sign[0].split()[1]:
                wish_wall = WishWall()
                wish_wall.wish_content = content[0]
                wish_wall.username = sign[0].split()[1]
                wish_wall.save()
        except Exception as e:
            pass


if __name__ == "__main__":
    for i in range(2, 18):
        source = get_source(i)
        main(source)



