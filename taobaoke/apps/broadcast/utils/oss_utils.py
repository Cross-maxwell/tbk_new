# coding=utf-8
import oss2

# 阿里云配置
oss_config = {
    'END_POINT': 'http://oss-cn-shenzhen.aliyuncs.com',
    'ACCESS_KEY_ID': 'LTAI9cS8Q51FXd4G',
    'ACCESS_KEY_SECRET': 'f3zkCCV0Yw6yTAepKxuFZKg2CgLRQI',
    'BUCKET_NAME': 'md-bot-service',
    'URL_BASE': 'http://md-oss.di25.cn/'
}


class OSSMgr(object):
    auth = oss2.Auth(oss_config['ACCESS_KEY_ID'], oss_config['ACCESS_KEY_SECRET'])
    bucket = oss2.Bucket(auth, oss_config['END_POINT'], oss_config['BUCKET_NAME'], connect_timeout=20)