# coding=utf-8
import json
import scrapy
import requests
import re


class GoodsSpider(scrapy.Spider):
    name = 'goodsspider'

    custom_settings = {
        'DOWNLOAD_DELAY': 2
    }

    start_urls = [
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=1&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=2&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=3&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=4&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=5&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=6&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=7&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=8&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=9&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=10&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=11&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=12&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=13&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=14&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=15&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=16&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=17&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=18&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=19&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=20&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=21&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=22&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=23&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=24&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=25&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=26&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=27&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=28&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=29&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=30&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=31&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=32&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=33&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=34&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=35&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=36&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=37&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=38&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=39&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=40&act=&keys=&cid=',
        'http://www.fuligou88.com/haoquan/ajax6.php?do=next&page=41&act=&keys=&cid=',
    ]
    convert_url = 'http://www.fuligou88.com/haoquan/details_show00.php?act=zhuan'

    def parse(self, response):
        # for good in response.css('div#list > table > tbody > tr > td:not(:empty)'):
            # yield {
            # 	'title': good.css('a div:nth-child(0)'),
            # 	'url': good.attr('href'),
            # 	'cupon_amount': good.css('td:nth-child(0)'),
            # 	'price': good.css('td:nth-child(1)'),
        # }

        def get_good_info(response):

            match_price = re.search(u'券后价￥([\d\.]+)元包邮', response.css('div.app > table tr:nth-child(2) > td > div > div:nth-child(1)').extract_first())
            price = match_price.group(1)
            match_cupon_value = re.search(u'节省: ([\d\.]+)元', response.css('div.app > table  tr:nth-child(2) > td > div > div:nth-child(2)').extract_first())
            cupon_value = match_cupon_value.group(1)
            match_sold_qty = re.search(u'已热销：(\d+)件', response.css('div.app > table tr:nth-child(3) > td > div:nth-child(1)').extract_first())
            sold_qty = match_sold_qty.group(1)

            rst_dict = {
                'title': response.css('input#title')[0].root.attrib['value'].strip(),
                'desc': response.css('div.app > table td > p')[0].root.text.strip(),
                'img_url': response.css('input#imgshow')[0].root.attrib['value'],
                'cupon_url': response.css('input#fuligou')[0].root.attrib['value'],
                'cupon_value': cupon_value,
                'price': price,
                'sold_qty': sold_qty,
            }
            requests.post('http://localhost:8000/product/insert/', data=json.dumps(rst_dict))
            yield rst_dict

        for good in response.css('table > tr > td > a'):
            good_url = response.urljoin(good.root.attrib['href'])
            yield scrapy.Request(good_url, callback=get_good_info)


