# -*- coding: utf-8 -*-

import os
import tornado
import tornado.ioloop
import tornado.httpserver
import tornado.web
import tornado.wsgi
import tornado.options
from django.core.wsgi import get_wsgi_application
import tornado.log

tornado.options.define('port', default=9090, help="run the given port", type=int)


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




