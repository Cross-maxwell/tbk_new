# coding: utf-8

from fuli.settings import DATABASES
import pymysql
class SQLHandler(object):
    cur_db = DATABASES['default']
    conn_dict = {
        'host': cur_db['HOST'],
        'port': int(cur_db['PORT']),
        'user': cur_db['USER'],
        'password': cur_db['PASSWORD'],
        'db': cur_db['NAME'],
        'charset': cur_db['OPTIONS']['charset'],
        # 'cursorclass' : pymysql.cursors.DictCursor,
    }

    @classmethod
    def execute(cls, sql_sentence, get_json=False):
        if get_json:
            conn = pymysql.connect(**dict(cls.conn_dict, cursorclass=pymysql.cursors.DictCursor))
        else:
            conn = pymysql.connect(**cls.conn_dict)
        cursor = conn.cursor()
        try:
            cursor.execute(sql_sentence)
            return cursor.fetchall()
        except:
            return None
        finally:
            cursor.close()
            conn.close()
