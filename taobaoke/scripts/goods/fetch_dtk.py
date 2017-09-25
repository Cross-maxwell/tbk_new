# coding=utf-8
import json
import scrapy
import requests
import re
import random


class GoodsSpider(scrapy.Spider):
    name = 'goodsspider'

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RETRY_TIMES': 8,
    }

    start_urls = [
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&u=543786',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=5&u=543786',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=1&u=543786',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=4&u=543786',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=8&u=543786',

        'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=1&s=lql',
        'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=9&s=lql',
        'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=10&s=lql',

        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=4&s=lql',
        'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=5&s=lql',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=7&s=lql',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=8&s=lql',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=9&s=lql',
        'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=4&u=543786',
        'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=4&s=sell',
        'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=7&s=sell',
        'http://s-prod-04.qunzhu666.com/dtk/?r=l&cid=7&s=lql',
        'http://s-prod-04.qunzhu666.com/dtk/?cid=8&s=lql&r=l&jgqj1=10&jgqj2=',
        

        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&t=1493598724&key=d2e4ddbf9df6104418bf859de9687031&kw=%E8%BE%BE%E8%8A%99%E5%A6%AE',        'http://s-prod-04.qunzhu666.com/dtk/?r=l&t=1493598741&key=880ef7d68afd3ea681ab04bc2c2c9aa7&kw=%E6%B5%AA%E8%8E%8E',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&t=1493598784&key=4d6df1bb6ebcf3a6583d3bf62f4636ab&kw=%E4%B8%83%E5%8C%B9%E7%8B%BC',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&t=1493598824&key=2e76b8083ff5bfd926bda05430efb6c6&kw=%E6%94%B6%E7%BA%B3',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=p&u=543786',
        # 'http://s-prod-04.qunzhu666.com/dtk/?r=l&t=1493599045&key=120a6cf6d4e39c2d1e894f5afffc2218&kw=361',

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
            try:
                print '----Get Item-----'
                img_url = response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > a > img')[0].root.attrib['src']
                price = response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > div.detail-col > div.coupon-wrap.clearfix > span.now-price > b:nth-child(2) > i').extract_first()
                cupon_value = response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > div.detail-col > div.ehy-normal.clearfix > div > span:nth-child(2) > b').extract_first()[1:]
                price_str = response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > div.detail-col > div.coupon-wrap.clearfix > span.now-price > b:nth-child(2) > i').extract_first()
                price = re.search('\d+', price_str).group(0)
                cupon_value_str = response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > div.detail-col > div.ehy-normal.clearfix > div > span:nth-child(2) > b').extract_first()
                cupon_value = re.search('\d+', cupon_value_str).group(0)
                sold_qty_str = response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > div.detail-col > div.text-wrap > span:nth-child(2) > i').extract_first()
                sold_qty = re.search('\d+', sold_qty_str).group(0)

                rst_dict = {

                    'title': response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > div.detail-col > a > span.title ::text').extract_first().strip(),
                    'desc': response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > div.detail-col > div.desc > span ::text').extract_first().strip(),
                    'img_url': response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > a > img')[0].root.attrib['src'],
                    'cupon_url': response.css('#dtk_mian > div.detail-wrap.main-container > div.detail-row.clearfix > div.detail-col > div.ehy-normal.clearfix > a')[0].root.attrib['href'],
                    'cupon_value': cupon_value,
                    'price': price,
                    'sold_qty': sold_qty,
                    'cupon_left': random.randint(50,200)
                }

                requests.post('http://localhost:8000/product/insert/', data=json.dumps(rst_dict))
                yield rst_dict
            except Exception:
                meta = response.meta
                retries = meta.get('RETRY_COUNT', 0)
                if retries < 5:
                    meta['RETRY_COUNT'] = retries + 1
                    yield scrapy.Request(response.url, callback=get_good_info, meta=meta)

        for good in response.css('div.goods-list.main-container > ul > li > a'):
            good_url = response.urljoin(good.root.attrib['href'])
            yield scrapy.Request(good_url, callback=get_good_info)

        next_page_url = response.css('a.next-page::attr(href)').extract_first()

        if next_page_url is not None:
            print '-----Next page-----', next_page_url
            meta = response.meta
            page = meta.get('PAGE', 1)
            if page < 5:
                meta['PAGE'] = page + 1
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse, meta=meta)
