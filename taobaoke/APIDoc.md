
接口文档规则：
    1. 请求的url完整路径
    2. 请求的方法： get, post, ...
    3. 数据格式： json, form-data
    4. 请求中包含的数据字段：
         例如：
             username 用户手机号
             password 用户密码
    5. 返回值(此项可按需进行忽略)

自用发单系统端口: 8080
果粉街端口： 9090
user_auth:
    1.登录：
        http://s-prod-04.qunzhu666.com:8080/auth/login/
        方法: POST
        参数: username, password
        格式: json

    2.注册：
        http://s-prod-04.qunzhu666.com:8080/auth/register/
        方法: POST
        格式: json
        参数：
            username
            password1
            password2
            verifyNum: 短信验证码

    3.发送短信：
        http://s-prod-04.qunzhu666.com:8080/auth/send_verifyNum/
        方法: POST
        格式: json
        参数：
            username: 手机号

    4.修改密码：
        http://s-prod-04.qunzhu666.com:8080/auth/reset/
        方法: POST
        格式: json
        参数：
            username
            new_password1
            new_password2
            verifyNum

    5.退出登录：
        http://s-prod-04.qunzhu666.com:8080/auth/logout/
        方法: get

ipad_weixin:
    1.获取二维码：
        http://s-prod-04.quinzhu666.com：8080/robot/getqrcode?username=136XXXXXXXX
        方法: GET
        参数：
            username: 用户手机号
    2.判断二维码是否被扫描：
        http://s-prod-04.qunzhu666.com:8080/robot/is_uuid_login?uuid=gZF8miqrkksZ9mrRk7mc
        方法: GET
        参数：
            uuid: 二维码uuid
        返回值：
            {
                "name": "\u6a02\u9633",
                "ret": "0"   为1时表示该二维码已扫描
            }

    3.用户所有的机器人以及在线情况：
        http://s-prod-04.quinzhu666.com:8080/robot/host_list?username=136XXXXXXXX
        方法: GET
        参数：
            username: 用户手机号
        返回数据格式：
            {
                "data":[
                    {
                        "group":[
                            "福利社XXXX",
                            "天猫福利社",
                            "测试福利社",
                            "天猫福利社3",
                            "天猫淘宝福利社"
                        ],
                        "name":"樂阳",
                        "ret":0         ret为0表示该机器人未上线
                    },
                    {
                        "group":[
                            "福利社",
                            "天猫福利社3",
                            "测试福利社"
                        ],
                        "name":"渺渺的",
                        "ret":0
                    }
                ],
            }
    4. 设置发单时间
        http://s-prod-04.quinzhu666.com:8080/tk/set_pushtime/
        方法: POST
        格式: json
        参数：
            {
                "interval_time": 5,  发单时间间隔
                "begin_time": "23:00", 开始发单时间
                "end_time": "22:00"   结束发单时间
            }
        返回结果：
            {
                "data":{
                    "is_valid":true,
                    "interval_time":5,
                    "end_time":"22:00",
                    "begin_time":"23:00"
                },
                "retCode":200
            }

    5. 果粉街设置红包口令
        http://s-prod-04.qunzhu666.com:9090/robot/define_sign_rule/
        方法： POST
        参数：
            keyword
            md_username  用户手机号
        返回结果：
            {"ret": 0} 表示发单群为空或添加失败
            {"ret": 1} 添加成功
























