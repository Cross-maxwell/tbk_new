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

    # detail_key_list = [
    #     "num_iid", "title", "pict_url", "reserve_price,", "zk_final_price",
    #     "user_type", "provcity", "item_url", "small_images", "seller_id",
    #     "volume", "nick", "cat_name", "cat_leaf_name"
    # ]

    detail_dict = {
        # 商品id
        "provcity": item_info["provcity"],
        "small_images": item_info["small_images"]["string"],
        "volume": item_info["volume"],
        "cat_name": item_info["cat_name"],
        "cat_leaf_name": item_info["cat_leaf_name"],
        # "item_id": item_info["num_iid"],
        # "title": item_info["title"],
        # "img_url": item_info["pict_url"],
        # "reserve_price": float(item_info["reserve_price"]),
        # "org_price": float(item_info["zk_final_price"]),
        # "user_type": item_info["user_type"],
        # "item_url": item_info["item_url"],
        # "seller_id": item_info["seller_id"],
        # "nick": item_info["nick"],
    }

    return detail_dict