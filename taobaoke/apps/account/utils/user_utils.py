# coding:utf-8

from rest_framework_jwt.serializers import User
from broadcast.models.user_models import  Adzone
from broadcast.serializers.user_serializers import AdzoneSerializer

def get_next_level_user(username):
    agent_user = User.objects.get(username=username)
    # 拿到所有下线
    sub_agent_list = User.objects.filter(tkuser__inviter_id=agent_user.id)
    return sub_agent_list

def get_ad_zone(key, value):
    """
    获取adzone序列,
    """
    try:
        if key == 'username':
            adzone = Adzone.objects.get(tkuser__user__username=value)
        elif key == 'adzone_id':
            adzone = Adzone.objects.get(pid__contains=adzone_id)
        return AdzoneSerializer(adzone).data

    except Exception, e:
        print '##get_ad_zone error:'+str(value)
        print e
        # traceback.print_exc()
        return None


def get_ad_id(username):
    """
    根据手机号获取ad_id
    :param username:
    :return:
    """
    try:
        ad_zone = get_ad_zone('username', username)
        ad_id = ad_zone['pid'].split('_')[3]
        return ad_id
    except Exception, e:
        return None