# coding:utf-8
# s-prod-07.qunzhu666.com :  iZwz9htulfr2g6ew7vejlwZ
# s-prod-09.qunzhu666.com : iZwz98yzmngkm4s9tcedwlZ
# adam : adam-B250M-D3H
# smart : zero

def getDB(mode='prod'):
    assert mode in ['test', 'prod', 'smart','adam_test'], "DB choosing mode can only be 'test' or 'prod'"

    db_prod = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {'charset': 'utf8mb4'},
            'NAME': 'mmt',
            'USER': 'root',
            'PASSWORD': 'Xiaozuanfeng',
            'HOST': 's-prod-02.qunzhu666.com',
            'PORT': '50001',
        }
    }

    db_smart = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {'charset': 'utf8mb4'},
            'NAME': 'new_taobaoke_sys',
            'USER': 'root',
            'PASSWORD': 'keyerror',
            "PORT": "3306",
            "HOST": "localhost"
        }
    }

    db_adam = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {'charset': 'utf8mb4'},
            'NAME': 'adam_test',
            'USER': 'root',
            'PASSWORD': 'qazwsx102938',
            "PORT": "3306",
            "HOST": "localhost"
        }
    }

    # 主机名到数据库配置的映射
    hostname_mapping = {
        "default": db_prod,
        "adam-B250M-D3H": db_adam,
        "zero": db_smart,
        "": {}
    }

    if mode=='prod':
        return hostname_mapping.get('default')
    elif mode=='adam_test':
        return hostname_mapping.get('adam-B250M-D3H')
    else:
        import socket
        hostname= socket.gethostname()
        return hostname_mapping.get(hostname, "")

