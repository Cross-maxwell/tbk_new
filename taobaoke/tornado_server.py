import os
import tornado
import tornado.ioloop
import tornado.httpserver
import tornado.web
import tornado.wsgi
import tornado.options
from django.core.wsgi import get_wsgi_application

tornado.options.define('port', default=8080, help="run the given port", type=int)


def main():
    tornado.options.parse_command_line()
    os.environ['DJANGO_SETTINGS_MODULE'] = 'fuli.settings'
    application = get_wsgi_application()
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container, xheaders=True)
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()


"""
[program:weixin_bot_02]
command=/home/smartkeyerror/.virtualenvs/django_env/bin/python /home/smartkeyerror/PycharmProjects/taobaoke/taobaoke/tornado_server.py --port=8081
directory=/home/smartkeyerror/PycharmProjects/taobaoke/taobaoke
autorestart=true
redirect_stderr=true
stdout_logfile=/home/smartkeyerror/weixin_bot.log
loglevel=info

[program:weixin_bot_03]
command=/home/smartkeyerror/.virtualenvs/django_env/bin/python /home/smartkeyerror/PycharmProjects/taobaoke/taobaoke/tornado_server.py --port=8082
directory=/home/smartkeyerror/PycharmProjects/taobaoke/taobaoke
autorestart=true
redirect_stderr=true
stdout_logfile=/home/smartkeyerror/weixin_bot.log
loglevel=info

[program:weixin_bot_04]
command=/home/smartkeyerror/.virtualenvs/django_env/bin/python /home/smartkeyerror/PycharmProjects/taobaoke/taobaoke/tornado_server.py --port=8083
directory=/home/smartkeyerror/PycharmProjects/taobaoke/taobaoke
autorestart=true
redirect_stderr=true
stdout_logfile=/home/smartkeyerror/weixin_bot.log
loglevel=info

"""