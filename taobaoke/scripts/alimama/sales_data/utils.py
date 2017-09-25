# -*- coding: utf-8 -*-
import oss2
import requests

oss_config = {
    'END_POINT': 'http://oss-cn-shenzhen.aliyuncs.com',
    'ACCESS_KEY_ID': 'LTAI9cS8Q51FXd4G',
    'ACCESS_KEY_SECRET': 'f3zkCCV0Yw6yTAepKxuFZKg2CgLRQI',
    'BUCKET_NAME': 'md-bot-service',
    'URL_BASE': 'http://md-bot-service.oss-cn-shenzhen.aliyuncs.com/'
}

auth = oss2.Auth(oss_config['ACCESS_KEY_ID'], oss_config['ACCESS_KEY_SECRET'])
bucket = oss2.Bucket(auth, oss_config['END_POINT'], oss_config['BUCKET_NAME'])


def put_file_to_oss(fn, data):
    """
    内部方法，用来直接将字符串数据存储到OSS的指定文件中
    :param fn: 文件的相对路径
    :param data: 文件的内容
    :return: 文件的外部地址
    """
    bucket.put_object_from_file(fn, data)
    return oss_config['URL_BASE'] + fn


def beary_chat(text, url=None, user=None, channel=None):
    requests.post(
        'https://hook.bearychat.com/=bw8NI/incoming/ab2346561ad4c593ea5b9a439ceddcfc',
        json={
            'text': text,
            "channel": channel,
            "user": user,
            "attachments": [
                {
                    "images": [{"url": url}]
                }
            ]
        }
    )