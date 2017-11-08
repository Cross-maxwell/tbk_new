# # coding:utf-8
# """
# *************************************************************
# 现已经不使用该脚本进行心跳维护，现使用的逻辑在heartbeat_manager.py中
# *************************************************************
#
# 每60对每个已登录用户心跳一次 并且拿到新的message 以用来筛选出激活群
# 部署在s-proc-04 supervisor上，可直接访问 s-prod-04.qunzhu666.com:9001 (admin/123456)
# """
# import sys
# # 脚本加入搜索路径 现在是hard code状态 看看有没有办法改
# sys.path.append('/Users/hong/sourcecode/work/ipad_wechat_test/wx_pad_taobaoke')
# sys.path.append('/home/ipad_wechat_test/wx_pad_taobaoke')
# print(sys.path)
# from taobaoke import weixin_bot
# from taobaoke.database import model
# from taobaoke import app
# import time
#
#
# def heartbeat_user():
#     with app.app_context():
#         user_list = model.User.query.filter(model.User.login > 0).all()
#         print([user.userame for user in user_list])
#         for user in user_list:
#             print(user.userame)
#             wx_bot = weixin_bot.WXBot()
#             try:
#                 if wx_bot.try_get_new_message(user.userame):
#                     print("suc in {}".format(user.userame))
#                 else:
#                     print("fail in {}".format(user.userame))
#             except Exception as e:
#                 print(e)
#
#
# if __name__ == "__main__":
#     while True:
#         try:
#             heartbeat_user()
#         except Exception as e:
#             print(e)
#         time.sleep(30)
