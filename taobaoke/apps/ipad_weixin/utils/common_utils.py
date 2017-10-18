# _*_ coding:utf-8 _*_
import re
import socket
from datetime import datetime
import time
import requests
import struct
import md5
# from pyv8 import PyV8
#
#
# def run_js(s):
#     ctxt = PyV8.JSContext()
#     ctxt.enter()
#     func = ctxt.eval("function asciiConvertNative(s){var asciicode=s.split(\"\\\\u\");var nativeValue=asciicode[0];for(var i=1;i<asciicode.length;i++){var code=asciicode[i];nativeValue+=String.fromCharCode(parseInt(\"0x\"+code.substring(0,4)));if(code.length>4){nativeValue+=code.substring(4,code.length)}}return nativeValue};")
#     print func(s)

RANDOM_ROUTER_DICT = {0:'TP_LINKS_5G', 1:'TP_LINK_5G', 2:'TP_LINK_2.4G', 3:'TP_LINKS_2.4G'}
RANDOM_COMMUNICATION_DICT = {0:'中国移动', 1:'中国联通', 2:'中国电信'}
def get_md5(s):
    if s == '' or s is None:
        return "74237af20c724e36316cf39ddce7a97c"
    m1 = md5.new()
    m1.update(s)
    return m1.hexdigest()


def get_time_stamp():
    ret = datetime.now().timetuple()
    return int(time.mktime(ret))


def byte_list_to_byte_string(byte_list):
    byte_string = ''
    for byte in byte_list:
        byte_string += byte
    return byte_string


def get_public_ip():
    # r = requests.get("http://1212.ip138.com/ic.asp")
    # reg = "\[(.*?)\]"
    # ip = re.findall(reg, r.text, re.M)[0]
    # return ip.replace('[', '').replace(']', '')
    return '119.23.149.138'


def usc2ascii(s):
    asciicode = s.split(r"\\u")
    nativeValue = asciicode[0]
    for i in range(1, len(asciicode)):
        code = asciicode[i]
        nativeValue += unichr(int('0x'+code[:4], 16))
        if len(code) > 4:
            nativeValue += code[4:]
    return nativeValue

# def read_int(byte_list, index):
#     if len(byte_list) >= 16:
#         seqBuf = byte_list[index:index + 4]
#         # str_to_convert = ''
#         # for byte in seqBuf:
#         #     print(byte)
#         #     str_to_convert += str(ord(byte))
#         # print(str_to_convert)
#         # # 32位正整数从网络序转换成主机字节序，整数与ip地址互换
#         # seq_int = struct.unpack('i', str_to_convert)[0]
#         seq_int = struct.unpack('I', seqBuf)[0]
#         return socket.ntohl(seq_int)
#     return 1
def read_int(byte_string_list, index):
    if len(byte_string_list) >= 16:
        seqBuf = byte_string_list[index:index + 4]
        seq_int = struct.unpack('I', seqBuf)[0]
        return socket.ntohl(seq_int)
    return 1


def int_list_convert_to_byte_list(int_list):
    # each num in int_list must lower than 256
    byte_str = ''
    for int_num in int_list:
        byte_str = byte_str + chr(int_num)
    return byte_str


def char_to_str(char_lst):
    s = ''
    for i in char_lst:
        s = s + i
    return s


def check_buffer_16_is_191(buffers):
    if buffers is None:
        return 0
    if ord(buffers[16]) is not 191:
        return 1
    else:
        return 2


def str_to_byte_list(s):
    byte_list = []
    for i in s:
        byte_list.append(ord(i))
    return byte_list


def check_grpc_response(ret):
    if ret >= 10000001:
        print "grpc error"


def timestamp_to_time(timestamp):
    print time.localtime(timestamp)

def random_mac(md_username):
    candidate = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    total = reduce(lambda x, y: int(x) + int(y), list(md_username))
    res = []
    for i in range(1,len(md_username)-1, 2):
        total += int(md_username[i])
        temp = candidate[total%16]
        total += int(md_username[i+1])
        temp += candidate[total%16]
        res.append(temp)
    total += int(md_username[-1])
    temp = candidate[total%16]
    total += int(md_username[1])
    temp += candidate[total%16]
    res.append(temp)
    return ":".join(res)

def random_devicetpye(md_username):
    try:
        int(md_username)
    except Exception as e:
        return "<k21>TP_lINKS_5G</k21><k22>中国移动</k22><k24>c1:cd:2d:1c:5b:11</k24>"
    template = "<k21>{0}</k21><k22>{1}</k22><k24>{2}</k24>"
    name = RANDOM_ROUTER_DICT[int(md_username[-1]) % 4]
    tel_com = RANDOM_COMMUNICATION_DICT[int(md_username[-1]) % 3]
    mac = random_mac(md_username)
    return template.format(name,tel_com,mac)

def random_uuid(md_username):
    try:
        int(md_username)
    except Exception as e:
        return "667D18B1-BCE3-4AA2-8ED1-1FDC19446567"
    candidate = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    total = reduce(lambda x, y: int(x) + int(y), list(md_username))
    res, temp = [], ""

    for i in range(1, 9):
        total += int(md_username[i])
        temp += candidate[total % 16]
    res.append(temp)
    for j in range(3):
        temp = ""
        for i in range(4):
            total += int(md_username[i])
            temp += candidate[total % 16]
        res.append(temp)
    temp = ""
    for i in range(11):
        total += int(md_username[i])
        temp += candidate[total % 16]
    res.append(temp)
    total += int(md_username[-1])
    res[-1] += candidate[total % 16]

    return "-".join(res)

if __name__ == "__main__":
    # byte_list = range(1, 20)
    # print(read_int(byte_list, 10))
    # byte_list = ['\x00', '\x00', 'A', '\xbe', '\x00', '\x10', '\x00', '\x01']
    # print char_to_str(byte_list)
    # print(get_md5(str(time.time())))
    # timestamp_to_time(1503371850)
    # print(get_md5())
    # print(get_time_stamp())
    print random_devicetpye('18620366927')
    print random_devicetpye('15723106823')
    print random_devicetpye('1896480499')
    print random_devicetpye('abdc')
    print random_uuid('18620366926')
    print random_uuid('15723106823')
    print random_uuid('abcd')
