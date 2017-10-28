# -*- coding: utf-8 -*-

from broadcast.views.entry_views import insert_broadcast_by_msg, insert_product_by_msg, \
    insert_product, search_product, push_product, search_product_pad
from broadcast.views.user_views import update_adzone, get_adzone_info, get_tkuser_info, \
    get_login_qrcode
from ipad_weixin.views.base_views import GetQrcode, HostList, IsUuidLogin, IsLogin, \
    DefineSignRule, AddSuperUser, ResetSingleHeartBeat, ResetHeartBeat
from broadcast.views.taobaoke_views import PostGoods, SendSignNotice, SetPushTime
from user_auth.views import LoginView, RegisterVIew, SendTextMessage, ResetPassword, Logout


# auth_user
login = ('http://s-prod-04.qunzhu666.com:8080/auth/login/', LoginView)
register = ('http://s-prod-04.qunzhu666.com:8080/auth/register/', RegisterVIew)
SendTextMessage = ('http://s-prod-04.qunzhu666.com:8080/auth/send_verifyNum/', SendTextMessage)
ResetPassword = ('http://s-prod-04.qunzhu666.com:8080/auth/reset/', ResetPassword)
Logout = ('http://s-prod-04.qunzhu666.com:8080/auth/logout/', Logout)

# ipad_weixin
GetQrcode = ('http://s-prod-04.quinzhu666.com：8080/robot/getqrcode?username=136XXXXXXXX', GetQrcode)
HostList = ('http://s-prod-04.quinzhu666.com:8080/robot/host_list?username=136XXXXXXXX', HostList)
IsUuidLogin = ('http://s-prod-04.qunzhu666.com:8080/is_uuid_login?uuid=gZF8miqrkksZ9mrRk7mc', IsUuidLogin)
IsLogin = ('http://s-prod-04.quinzhu666.com:8080/robot/is_login?username=md_username', IsLogin)

ResetHeartBeat = ('http://s-prod-04.qunzhu666.com:8080/robot/reset_heart_beat', ResetHeartBeat)
ResetSingleHeartBeat = ('http://s-prod-04.qunzhu666.com:8080/robot/reset_single?username=wx_id', ResetSingleHeartBeat)

DefineSignRule = ('http://s-prod-04.qunzhu666.com:8080/robot/define_sign_rule', DefineSignRule)

# tk
PostGoods = ('http://s-prod-04.qunzhu666.com:8080/tk/push_product', PostGoods)

SendSignNotice = (r'http://s-prod-04.qunzhu666.com:8080/tk/send_signin_notice', SendSignNotice)
SetPushTime = (r'http://s-prod-04.qunzhu666.com:8080/tk/set_pushtime', SetPushTime)

