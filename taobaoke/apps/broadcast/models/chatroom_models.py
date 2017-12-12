from django.db import models


class ChatRoomQrcode(models.Model):
    chatroom_id = models.CharField(max_length=25)
    name = models.CharField(max_length=100, null=True, default='')
    qrcode_url = models.CharField(max_length=200, null=True, default='')
    create_time = models.DateTimeField(null=True)
