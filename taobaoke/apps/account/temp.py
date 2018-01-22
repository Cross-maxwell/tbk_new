
# required by order_utils.py

# tbk_getusername_url = 'http://s-prod-04.qunzhu666.com:8000/user/get-tkuser-info/'
# tbk_getpid_url = 'http://s-prod-04.qunzhu666.com:8000/user/get-adzone-info/'

tbk_alipay_transfer_url_bak = 'https://pin.guofenjie.cn/365/api/alipay/transfer?account={0}&name={1}&amount={2}'
tbk_alipay_transfer_url = 'http://localhost:9999?alipay_account={0}&alipay_name={1}&amount={2}&out_biz_no={3}'

# required by order_views.py
admin_phone = '15002086851'

luosimao_kye = 'key-8fe86c39fce8f0d75de9373cd9e837f5'
def send_message(phoneNum, message):
    return_value = False
    resp = requests.post("http://sms-api.luosimao.com/v1/send.json",
                         auth=("api", settings.luosimao_kye),
                         data={
                             "mobile": phoneNum,
                             "message": message
                         }, timeout=3, verify=False)
    result = json.loads(resp.content)
    if result['error'] == 0:
        return_value = True
    return return_value
