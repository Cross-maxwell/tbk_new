# coding=utf-8
from broadcast.models.entry_models import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.db.models import Q
import logging
import threading
import time
logger = logging.getLogger('post_taobaoke')


class WebDriverBot(object):
    def __init__(self, user):
        self.user = user
        self.driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])

    def get_qrcode(self):
        self.driver.get('https://wx.qq.com')
        time.sleep(3)
        self.driver.save_screenshot('login.png')
        elem = self.driver.find_element_by_css_selector('div.qrcode > img')
        return elem.get_attribute('src').split('/')[-1]

    def __run(self):
        while True:
            self.tick()
            time.sleep(20)

    def run(self):
        import thread
        thread.start_new_thread(self.__run)

    def tick(self):
        # 查数据库
        qs = Product.objects.filter(
            ~Q(pushrecord__group__contains=self.user.username,
               pushrecord__create_time__gt=timezone.now() - datetime.timedelta(days=3)),
            available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
        )

        # 用发送过的随机商品替代
        if qs.count() == 0:
            qs = Product.objects.filter(
                available=True, last_update__gt=timezone.now() - datetime.timedelta(hours=4),
            )
            # beary_chat('点金推送商品失败：无可用商品')

        for _ in range(50):
            try:
                r = random.randint(0, qs.count() - 1)
                p = qs.all()[r]
                break
            except Exception as exc:
                print "Get entry exception. Count=%d." % qs.count()
                logger.error(exc)
        # Get PID
        pid = self.user.tkuser.adzone.pid

        # Def helper function
        def send_multiline(elem, text):
            ts = text.split('\n')
            elem.send_keys(ts[0])
            for t in ts[1:]:
                elem.send_keys(Keys.SHIFT, Keys.ENTER)
                elem.send_keys(t)
            elem.send_keys(Keys.ENTER)

        # Filter groups
        msgs = self.driver.find_elements_by_css_selector('div.chat_item')
        for msg_item in msgs:
            if u'File Transfer' in msg_item.find_element_by_css_selector('.nickname_text').text:
                # Send img

                msg_item.click()

                self.driver.execute_script('$("input[type=file]").removeAttr("multiple");')
                file_upload_input = self.driver.find_element_by_css_selector('input[type=file]')
                file_upload_btn = self.driver.find_element_by_css_selector('a.web_wechat_pic')
                file_upload_btn.click()
                fn = '/tmp/%s-%s-%s' % (self.user.username, time.time(), p.get_img_msg().split('/')[-1])
                open(fn, 'wb').write(requests.get(p.get_img_msg()).content)
                file_upload_input.send_keys(fn)
                time.sleep(3)

                edit_area = self.driver.find_element_by_css_selector('#editArea')
                edit_area.click()
                send_multiline(edit_area, p.get_text_msg(pid))


