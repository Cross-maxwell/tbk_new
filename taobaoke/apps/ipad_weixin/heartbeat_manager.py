# _*_ coding:utf-8 _*_
import pickle

import weixin_bot
from settings import red
from utils import common_utils

import time
import threading

from utils import oss_utils
from models import *

import logging
logger = logging.getLogger('weixin_bot')


class HeartBeatManager(object):
    heartbeat_thread_dict = {}

    def __init__(self):
        pass

    def run(self):
        t = threading.Thread(target=self.__start_thread_pool)
        t.setDaemon(True)
        t.start()

    @staticmethod
    def __print_log(msg, title='heart_beat'):
        print '[{}]'.format(title) + msg

    @staticmethod
    def begin_heartbeat(vx_username):
        if vx_username in HeartBeatManager.heartbeat_thread_dict.keys():
            t = HeartBeatManager.heartbeat_thread_dict[vx_username]
            if t.isAlive():
                return

        t = threading.Thread(target=HeartBeatManager.heartbeat, name=vx_username, args=(vx_username,))
        HeartBeatManager.heartbeat_thread_dict[vx_username] = t
        t.setDaemon(True)
        t.start()
        # print "heartbeat start working..."

    def __start_thread_pool(self):
        online_user_list = WxUser.objects.filter(login__gt = 0).all()
        print([user.username for user in online_user_list])
        for user in online_user_list:
            HeartBeatManager.begin_heartbeat(user.username)

    def __detect_thread_pool(self):
        # TODO:定时检测线程是否异常
        pass

    @classmethod
    def heartbeat(cls, wx_username):
        is_first = True
        wx_bot = weixin_bot.WXBot()
        wx_bot.set_user_context(wx_username)

        # 微信有新消息就会往socket推20字节的notify包
        # 防止该socket断开，每30秒发一次同步消息包
        heart_beat_count = 0
        while True:
            try:
                user = WxUser.objects.filter(username=wx_username).first()
                if user is not None:
                    # 用户退出登陆,退出线程
                    if user.login == 0 and wx_bot._auto_retry == 30:
                        logger.info("{}: 用户重启心跳失败,结束心跳".format(user.nickname))
                        oss_utils.beary_chat("淘宝客{0}: 用户重启心跳失败，机器人已下线".format(user.nickname))
                        # 登出时需要把socket断开，否则会一直收到退出登陆的消息
                        wx_bot.wechat_client.close_when_done()
                        return

                if not wx_bot.wechat_client.connected:
                    # 测试过后发现好像没有哪个包能阻止socket断开，断开只是时间问题
                    # 检测一下socket有没断开，如果断开，重新起一个socket即可
                    # oss_utils.beary_chat("{} heart_beat socket 断开, 准备重新链接".format(wx_username), user='fatphone777')
                    # cls.__print_log("{0} socket state:{1}".format(wx_username, wx_bot.wechat_client.connected))
                    # oss_utils.beary_chat("淘宝客{0}: socket断开，尝试进行二次登录".format(user.nickname))
                    # logger.info("{0}: socket断开，尝试重新进行二次登录".format(user.nickname))
                    # wx_bot.wechat_client.close_when_done()
                    time.sleep(5)
                    # 再一次初始化
                    is_first = True
                    temp = wx_bot._auto_retry
                    wx_bot = weixin_bot.WXBot()
                    wx_bot._auto_retry = temp
                    wx_bot.set_user_context(wx_username)
                    wx_bot.open_notify_callback()


                v_user = pickle.loads(red.get('v_user_' + wx_username))

                if is_first:
                    UUid = user.uuid
                    DeviceType = user.device_type
                    start_time = datetime.datetime.now()
                    logger.info("%s: 进行心跳二次登录中" % user.nickname)
                    while True:
                        res_auto = wx_bot.auto_auth(v_user, UUid, DeviceType, False)
                        if res_auto is True:
                            wx_bot.open_notify_callback()
                            logger.info("{}: 心跳二次登录成功".format(user.nickname))
                            oss_utils.beary_chat("淘宝客{0}: 机器人已上线, 心跳开启成功--{1}".format(user.nickname, int(time.time())))
                            break
                        elif res_auto is 'Logout':
                            logger.info("{}: 用户主动退出登录，退出心跳，机器人下线".format(user.nickname))
                            oss_utils.beary_chat("淘宝客{0}: 用户主动退出登录，退出机器人".format(user.nickname))
                            # wx_bot.wechat_client.close_when_done()
                            wx_bot.logout_bot(v_user)
                            return

                        logger.info("%s: 心跳重试二次登录中" % user.nickname)
                        if (datetime.datetime.now() - start_time).seconds >= 100:
                            oss_utils.beary_chat("{}: 心跳二次登录失败".format(user.nickname),
                                               user='fatphone777')
                            logger.info("{}: 心跳二次登录失败，退出心跳，登录失败".format(user.nickname))
                            oss_utils.beary_chat("淘宝客{0}: 啊哦，机器人心跳失败，上线失败".format(user.nickname))
                            # wx_bot.wechat_client.close_when_done()
                            wx_bot.logout_bot(v_user)
                            return
                        time.sleep(5)
                    is_first = False

                # c# demo 中的heart_beat包，能延长socket的持续时间
                # 但始终会断开
                if wx_bot._lock.acquire():
                    logger.info("%s: 开始发送心跳包" % user.nickname)
                    start_time = datetime.datetime.now()
                    if wx_bot.heart_beat(v_user):
                        # print "success"
                        logger.info("%s: 心跳包发送成功" % user.nickname)
                        heart_beat_count += 1

                        if heart_beat_count % 10 == 0:
                            user.last_heart_beat = timezone.now()
                            user.save()
                    else:
                        # print "fail"
                        logger.info("%s: 心跳包发送失败" % user.nickname)
                    # 如果心跳超过10分钟才发送完毕，认定socket阻塞了，重启心跳
                    if (datetime.datetime.now() - start_time).seconds > 10*60:
                        wx_bot.wechat_client.connected = False
                        logger.info("%s: 心跳完成发送超时，尝试重启心跳" % user.nickname)

                    wx_bot._lock.release()
                # print "{} heart best finished".format(wx_username)
                time.sleep(30)
            except Exception as e:
                logger.error(e)
                logger.info("[{0}]heartbeat exception:{1}".format(wx_username, e.message))
                continue

