# -*- coding:utf-8 -*-
import top.api
from fuli.top_settings import app_key,app_secret

# taobao.tbk.item.get (淘宝客商品查询)
# http://open.taobao.com/docs/api.htm?spm=a219a.7395905.0.0.gqyYhL&apiId=24515
# u'537645768649'
def get_item_info(item_id = "537645768649"):
    an_api = top.api.TbkItemInfoGetRequest
    req=an_api()
    req.set_app_info(top.appinfo(app_key,app_secret))
    req.fields="num_iid," \
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
    req.num_iids=item_id
    resp= req.getResponse()
    item_info = resp['tbk_item_info_get_response']['results']['n_tbk_item'][0]
    for i in item_info.keys():
        print "%s  :  %s"% (i,item_info[i])




if __name__=="__main__":
    get_item_info()

"""
{u'string': [u'http://img2.tbcdn.cn/tfscom/i4/2898637376/TB20mExhWagSKJjy0FaXXb0dpXa_!!2898637376.jpg', 
u'http://img4.tbcdn.cn/tfscom/i3/2898637376/TB24QxoggoQMeJjy0FnXXb8gFXa_!!2898637376.jpg', 
u'http://img1.tbcdn.cn/tfscom/i2/2898637376/TB2Y_Z.j6ihSKJjy0FiXXcuiFXa_!!2898637376.jpg', 
u'http://img2.tbcdn.cn/tfscom/i4/2898637376/TB257AFjBcHL1JjSZFBXXaiGXXa_!!2898637376.jpg']}
"""