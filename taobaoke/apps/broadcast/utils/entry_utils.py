# -*- coding: utf-8 -*-
import top.api
from fuli.top_settings import app_secret, app_key


def get_item_info(item_id):
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