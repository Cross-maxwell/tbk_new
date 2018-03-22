# coding: utf-8

"""
支付宝python sdk,第三方来源, 主页：https://github.com/fzlee/alipay/blob/master/README.zh-hans.md
"""
import time, os
from datetime import datetime
from alipay import AliPay
from fuli.top_settings import alipay_appid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def pay(account, name, amount):

    alipay = AliPay(
        appid=alipay_appid,
        app_notify_url='',
        app_private_key_path=os.path.join(BASE_DIR, 'utils/ali_private_key.pem'),
        alipay_public_key_path=os.path.join(BASE_DIR, 'utils/ali_public_key.pem'),
        sign_type="RSA2"
    )

    result = alipay.api_alipay_fund_trans_toaccount_transfer(
        out_biz_no= str(int(time.mktime(datetime.now().timetuple()))),
        payee_type="ALIPAY_LOGONID",
        payee_account=account,
        payee_real_name=name,
        amount=amount,
        payer_show_name='一起赚佣金',
    )

    return result