from django.test import TestCase
from mini_program.models.payment_models import PaymentOrder, Payment, AppUser, AppSession, UserAddress
from broadcast.models.entry_models import Product


class PaymentOrderTest(TestCase):
    def test_payment_order(self):
        app_user = AppUser.objects.create(nickname="session_key", openid="session_key")
        product = Product.objects.get(id=1)
        goods_num = 2
        total_fee = int((product.price * int(goods_num)) * 100)

        payment_order_dict = {
            "goods_id": product.id,
            "item_id": product.item_id,
            "goods_num": goods_num,
            "goods_title": product.item_id,
            "goods_price": product.price,
            "should_pay": total_fee,
            "app_user": app_user
        }
        payment_order = PaymentOrder.objects.create(**payment_order_dict)