# Best wishes to the arrogant programmer

from unittest import TestCase
from broadcast.utils.third_msg_utils import *

cases = [
    u'宜蜂尚 早餐营养水果麦片418*2袋~2袋~2袋【53.9元】券后【13.9元】包邮:https://shop.m.taobao.com/shop/coupon.htm?activityId=98b66df5a0874f2f8403370ccc0f5fec&sellerId=2216075099 下单链接: https://s.click.taobao.com/QBSFSTw 璃材质，做工精湛，通透晶莹，杯口圆滑平整，经久耐用，易清洗，酒店、家用都是不错的选择~【赠运费险】',
    u'【韵之堂】淘米水黑米浆修复发2瓶淘抢购29元，券后【19元】包邮买1送1共2瓶！改善毛躁，强韧防断发，染烫受损护，古方养发，无化学无色素无刺激，精华滋养，重现秀发年轻光彩【赠运费险】领取10元优惠券:https://shop.m.taobao.com/shop/coupon.htm?activityId=86a1ad32a6214befafac6a1882d3d479&sellerId=1039215743 下单链接:https://detail.tmall.com/item.htm?id=40400933903&ali_trackid=2:mm_15673656_16160355_60680148:1520333698_392_2088815926&pvid=12506817&skuId=76041692487',
    u'宜蜂尚取15元优惠券:https://shop.m.taobao.com/shop/coupon.htm?activityId=86a1ad32a6214befafac6a1882d3d479&sellerId=1039215743 下单链接: https://s.click.taobao.com/lfJHSTw 厚玻',
]


class Test3rdMsg(TestCase):
    def test_3rd_msg(self):
        for c in cases:
            m = WQMsg(c)
            m.parse()
            self.assertIsNotNone(m.item_id, m.item_url)
