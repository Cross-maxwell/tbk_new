# coding=utf-8
from functools import wraps, update_wrapper
from flask import Flask, request, current_app, jsonify, make_response
from datetime import timedelta
import sys
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
app = Flask(__name__)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


def support_jsonp(f):
    """Wraps JSONified output for JSONP"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f().data) + ')'
            return current_app.response_class(content, mimetype='application/json')
        else:
            return f(*args, **kwargs)

    return decorated_function


# then in your view
@app.route('/kfc/test', methods=['GET'])
@support_jsonp
def test():
    # return jsonify({"foo": "bar"})
    return jsonify({"act_id": "4", "redurl": "http://d.xiumi.us/board/v5/2FdPf/48769691",
                    "srcurl": "http://d.xiumi.us/board/v5/2FdPf/48769691",
                    "tgurl": "http://i1.buimg.com/1949/83a0adce734f5853.png",
                    "url": "http://i1.buimg.com/1949/83a0adce734f5853.png",
                    "whdate": "7月10日",
                    "xbimg": ""})


# 上传到服务器
@app.route('/swagger/upload/<project>', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def saveFile(project):
    try:
        f = open('/home/prod/swagger_file/' + project + '.yaml', 'w+')
        f.write(request.form['the_file'])
        f.close()
        return jsonify(retCode=200)
    except:
        traceback.print_exc()


# 读取返回到接口
@app.route('/swagger/content/<project>', methods=['GET'])
@crossdomain(origin='*')
def readfile(project):
    f = open('/home/prod/swagger_file/' + project + '.yaml', 'r')
    if f:
        str = f.read()
    else:
        str = ''
    f.close()
    return jsonify(retCode=200, data=str)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
