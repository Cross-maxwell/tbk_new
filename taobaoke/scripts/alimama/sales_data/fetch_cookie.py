# -*- coding: utf-8 -*-
import datetime
import os
import time
from selenium import webdriver
from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.common.action_chains import ActionChains
from utils import beary_chat
import utils
import requests
from PIL import Image

PHANTOM_JS_PATH = '/usr/bin/phantomjs'
COOKIES_PATH = '/home/new_taobaoke/taobaoke/scripts/alimama/cookie.txt'
ADMIN_NAME = "Chong"

def fetch_cookie_fromfile():
    # 读取cookie文件
    with open(COOKIES_PATH, 'r') as f:
        cookie_str = f.read()
    print cookie_str.strip()
    return cookie_str.strip()


def detect_cookie(cookie_str, url):
    resp = requests.get(
        url=url,
        headers={'Cookie': cookie_str}
    )

    if 'html' in resp.text:
        # 说明cookie失效
        print('cookie无效')
        return False
    return True


def save_cookie_to_file(cookie_str, file_path):
    with open('file_path', 'wb') as f:
        f.write(cookie_str)
    print cookie_str.strip()
    return cookie_str.strip()


def fetch_cookie_from_network():
    # website element location args
    qrcode_btn_x = 1205
    qrcode_btn_y = 132
    qrcode_region = (907, 81, 1261, 399)

    url_login = 'https://www.alimama.com/member/login.htm'
    phantom_js_driver_file = os.path.abspath(PHANTOM_JS_PATH)
    if os.path.exists(phantom_js_driver_file):
    # if True:
        try:
            print('loading PhantomJS from {}'.format(phantom_js_driver_file))
            driver = webdriver.PhantomJS(phantom_js_driver_file)
            # driver = webdriver.PhantomJS()
            driver.set_window_size(1640, 688)
            driver.get(url_login)
            print('opening pub_alimama login page, this is first done for prepare for cookies. be patience to waite '
                  'load complete. wait 20s')
            #driver.save_screenshot('before_login.png')
            # 现在直接打开页面就显示二维码,不需要进行点击..
            # 切换到扫码的按钮在屏幕中的位置
            # ActionChains(driver).move_by_offset(qrcode_btn_x, qrcode_btn_y).click()\
            #     .move_by_offset(-qrcode_btn_x, -qrcode_btn_y).perform()
            # time.sleep(2)

            # 需要移动一下才能比较快的显示出来...
            ActionChains(driver).move_by_offset(2, 3).move_by_offset(-2, -3).perform()
            time.sleep(2)
            driver.save_screenshot('before_login.png')
            print('qrcode have generated')

            file_name = 'qrcode.png'
            img = Image.open('before_login.png')
            img.crop(qrcode_region).save(file_name)
            upload_png_name = 'qrcode-{}.png'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M%S'))
            oss_path = utils.put_file_to_oss(upload_png_name, file_name)
            print('screen.png saved' + oss_path)

            cur_url = driver.current_url
            print('send bearychat')
            beary_chat('日入3000！', oss_path, user=ADMIN_NAME)
            beary_chat('日入3000！', oss_path, user="fatphone777")

            # alimama qrcode refresh interval is 120s
            detect_times = 30
            while driver.current_url == cur_url and detect_times != 0:
                time.sleep(3)
                detect_times -= 1

            if detect_times == 0:
                print(ADMIN_NAME + " didn't logged in")
                driver.quit()
                return False
            else:
                driver.save_screenshot('login.png')
                cookie_list = driver.get_cookies()
                cookie_string = ''
                for cookie in cookie_list:
                    if 'name' in cookie and 'value' in cookie:
                        cookie_string += cookie['name'] + '=' + cookie['value'] + '; '
                print('success get cookies!! \n{}'.format(cookie_string))

                with open(COOKIES_PATH, 'w') as f:
                    f.write(cookie_string)

                beary_chat("销售数据正在更新中～", channel=u"淘宝客")
                driver.quit()
                return True
        except InvalidElementStateException as e:
            print(e)
            return False
    else:
        print('can not find PhantomJS driver, please download from http://phantomjs.org/download.html based on your '
              'system.')
        return False

if __name__ == '__main__':
    # cookie_string = fetch_cookie_from_network()
    # cookie_string = fetch_cookie_fromfile()
    pass
