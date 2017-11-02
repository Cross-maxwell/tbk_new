# coding=utf-8
import top.api
from fuli.top_settings import *
import json

class Item_info(object):
    '''
    文档地址:http://open.taobao.com/docs/api.htm?spm=a219a.7629065.0.0.UNFPYN&apiId=24518&scopeId=11655
    返回的字段很齐全,目前只写了急用的
    '''
    def __init__(self,item_id):
        req=top.api.TbkItemInfoGetRequest()
        req.set_app_info(top.appinfo(app_key, app_secret))
        req.fields = "num_iid,title,pict_url,small_images,reserve_price,zk_final_price,user_type,provcity,item_url,volume, cat_name,cat_leaf_name"
        req.num_iids=str(item_id)
        try:
            resp =req.getResponse()
            self.detail = resp['tbk_item_info_get_response']['results']['n_tbk_item'][0]
        except Exception, e:
            print(e)

    @property
    def item_id(self):
        return self.detail['num_iid']

    @property
    def title(self):
        return self.detail['title']

    @property
    def img_url(self):
        return self.detail['pict_url']

    @property
    def small_images(self):
        return self.detail['small_images']

    @property
    def sold_qty(self):
        return self.detail['volume']



