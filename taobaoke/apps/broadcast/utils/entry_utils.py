# -*- coding: utf-8 -*-
import top.api
from fuli.top_settings import app_secret, app_key
from django.core.cache import cache
import logging

def get_item_info(item_id):
    try:
        an_api = top.api.TbkItemInfoGetRequest
        req = an_api()
        req.set_app_info(top.appinfo(app_key, app_secret))
        req.fields = "num_iid," \
                     "title," \
                     "pict_url," \
                     "reserve_price," \
                     "zk_final_price," \
                     "user_type,"  \
                     "provcity," \
                     "item_url," \
                     "small_images," \
                     "seller_id," \
                     "volume," \
                     "nick," \
                     "cat_name," \
                     "cat_leaf_name"
        req.num_iids = item_id
        resp = req.getResponse()
        item_info = resp['tbk_item_info_get_response']['results']['n_tbk_item'][0]
        return item_info
    except Exception as e:
        logging.error(e)
        return None

def get_cupon_info(item_id, activity_id):
    an_api = top.api.TbkCouponGetRequest
    req = an_api()
    req.set_app_info(top.appinfo(app_key, app_secret))
    req.item_id = item_id
    req.activity_id = activity_id
    try:
        resp = req.getResponse()
        return resp['tbk_coupon_get_response']['data']
    except Exception, e:
        return None


class HandlePushFIFO(object):
    """
    A fifo for user to handle push max to 10 elements.
    Each elements should be a list, contains msg to send.
    Sample:
        User A pushed 5 product in a row, msg of each product is a list which contains
        the product's text , img , and app msg.
        So the fifo should be a list contains 5 lists, each sublist contains all msg of a product.
    The FIFO has two methods:
        1. push: push an element to the end of  the FIFO,
        2. fetch: get an element from the start of the FIFO.
    """

    fifo_name = 'handle_push_fifo_{}'
    def __init__(self, username):
        self.fifo_name = HandlePushFIFO.fifo_name.format(username)
        self.username = username
        self.fifolist = cache.get(self.fifo_name)
        if not self.fifolist:
            self.fifolist = []
            cache.set(self.fifo_name, self.fifolist)

    def __repr__(self):
        return '<Handle Push FIFO of {}>'.format(self.username)

    def push(self, msg_list):
        assert type(msg_list) == list, 'The param should be a list.'
        if self.length < 10:
            self.fifolist.append(msg_list)
            cache.set(self.fifo_name, self.fifolist)
        else: raise FIFOTooLongException(self.length)

    def fetch(self):
        try:
            resp = self.fifolist.pop(0)
            cache.set(self.fifo_name, self.fifolist)
            return resp
        except IndexError:
            return None

    def undofetch(self, msg_list):
        self.fifolist.insert(0, msg_list)
        cache.set(self.fifo_name, self.fifolist)

    @property
    def length(self):
        return len(self.fifolist)

class FIFOTooLongException(Exception):
    def __init__(self, length):
        self.message = "FIFO's length can't beyond 10, it's already {} now.".format(length)
        Exception.__init__(self, self.message)
