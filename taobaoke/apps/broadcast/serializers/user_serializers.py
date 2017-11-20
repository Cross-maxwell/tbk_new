from broadcast.models.user_models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
        )


class AdzoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adzone
        fields = (
            'pid', 'adzone_name',
            'click_30d', 'alipay_num_30d', 'rec_30d', 'alipay_rec_30d',
            'last_update',
        )


class TkUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TkUser
        fields = (
            'user', 'adzone', 'avatar_url', 'invite_code', 'inviter_id', 'inviter_backup_info'
        )
