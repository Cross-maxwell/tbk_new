# coding:utf-8

"""
Django settings for fuli project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)


import sys
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tdw1=k(f2=%^*9bj*_+h_05(!wk03^(_jto+m0t6322uo!2y-('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['s-prod-04.qunzhu666.com', 'localhost', 'tmp.zhiqun365.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'broadcast',
    'rest_framework',
    'corsheaders',
    'user_auth',
    'account'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',   # 跨域解决方案
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]



ROOT_URLCONF = 'fuli.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'apps/broadcast/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'broadcast.jinja2env.environment',
            # 'context_processors': [
            #     'django.template.context_processors.debug',
            #     'django.template.context_processors.request',
            #     'django.contrib.auth.context_processors.auth',
            #     'django.contrib.messages.context_processors.messages',
            # ],
        },
    },
]

WSGI_APPLICATION = 'fuli.wsgi.application'

from broadcast.views.server_settings import REDIS_PORT, S_POC_01_INT
REDIS_SERVER = S_POC_01_INT

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'redis://'+ REDIS_SERVER +':' + str(REDIS_PORT),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}


CSRF_COOKIE_SECURE = True
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

from fuli.config import getDB
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'OPTIONS': {'charset': 'utf8mb4'},
#         'NAME': 'mmt',
#         'USER': 'root',
#         'PASSWORD': 'Xiaozuanfeng',
#         'HOST': 's-prod-02.qunzhu666.com',
#         'PORT': '50001',
#     }
# }

# 可使用mode指定要使用的数据库。指定mode为'prod'，使用生产数据库; 指定为'test'或留空，将根据主机名进行选择。
# 配置请查看fuli/config.py
DATABASES = getDB(mode='smart')


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# 跨域解决方案
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ('*',)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/


# STATIC_ROOT = '/home/smartkeyerror/.virtualenvs/django_env/local/lib/python2.7/site-packages/django/contrib/admin/'
STATIC_URL = '/static/'


import logging
import django.utils.log
import logging.handlers

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
       'standard': {
            'format': '%(asctime)s [%(threadName)s] [%(name)s:%(funcName)s] [%(levelname)s]- %(message)s'}  #日志格式
    },
    'filters': {
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log', 'error.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console':{
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },


    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'django_models': {
            'handlers': ['error', 'console'],
            'level': 'ERROR',
            'propagate': True
        },
        'django_views': {
            'handlers': ['error', 'console'],
            'level': 'INFO',
            'propagate': True
        },
        'weixin_bot': {
            'handlers': ['error', 'console'],
            'level': 'INFO',
            'propagate': True
        },
        'post_taobaoke': {
            'handlers': ['error', 'console'],
            'level': 'INFO',
            'propagate': True
        },
        'entry_views': {
            'handlers': ['error', 'console'],
            'level': 'INFO',
            'propagate': True
        },
        'utils': {
            'handlers': ['error', 'console'],
            'level': 'INFO',
            'propagate': True
        },
        'sales_data': {
            'handlers': ['error', 'console'],
            'level': 'INFO',
            'propagate': True
        },
        'fetch_lanlan': {
            'handlers': ['error', 'console'],
            'level': 'INFO',
            'propagate': True
        },

    }
}
