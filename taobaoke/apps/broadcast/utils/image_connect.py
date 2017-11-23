# -*- coding: utf-8 -*-

from PIL import Image
import os
import requests
import urllib2
from io import BytesIO



def generate_qrcode(product_id, tkl):
    # 根据url生成二维码, 返回二维码的url
    pass


def connect_image():

    # 首先调用二维码生成函数


    # 新建画布
    toImage = Image.new('RGBA', (600, 1100))

    # 获取二维码
    qrcode_url = "http://md-bot-service.oss-cn-shenzhen.aliyuncs.com/wxpad/QdQYMvde-n0vpFse5TrO.png"
    data = urllib2.urlopen(qrcode_url).read()
    qrcode_img = Image.open(BytesIO(data))
    qrcode_size = qrcode_img.resize((200, 200))
    qrcode_location = (0, 900)
    toImage.paste(qrcode_size, qrcode_location)

    # 获取商品主图
    product_url = "http://oss3.lanlanlife.com/eed86f7a8731d12c3a8173cff019a309_800x800.jpg?x-oss-process=image/resize,w_600/format,jpg/quality,Q_80"
    product_data = urllib2.urlopen(product_url).read()
    product_img = Image.open(BytesIO(product_data))
    product_size = product_img.resize((600, 600))
    product_location = (0, 0)
    toImage.paste(product_size, product_location)


    # 商品附图
    url02 = "https://img.alicdn.com/imgextra/i1/2255978310/TB2GEBPnjuhSKJjSspdXXc11XXa_!!2255978310.jpg_430x430q90.jpg"
    url02_data = urllib2.urlopen(url02).read()
    url02_img = Image.open(BytesIO(url02_data))
    url02_size = url02_img.resize((300, 300))
    url02_location = (0, 600)
    toImage.paste(url02_size, url02_location)

    url03 = "https://img.alicdn.com/imgextra/i2/2255978310/TB2oBGvnjuhSKJjSspmXXcQDpXa_!!2255978310.jpg_430x430q90.jpg"
    url03_data = urllib2.urlopen(url03).read()
    url03_img = Image.open(BytesIO(url03_data))
    url03_size = url03_img.resize((300, 300))
    url03_location = (300, 600)
    toImage.paste(url03_size, url03_location)

    # 获取长按扫描图# 将图片进行拼接
    saomiao_img = Image.open('lingqu.jpg')
    saomiao_size = saomiao_img.resize((400, 200))
    saomiao_location = (200, 900)
    toImage.paste(saomiao_size, saomiao_location)

    # 将图片进行拼接
    print(toImage.size)
    print toImage
    toImage.save('merged.png')

connect_image()


# # 图片压缩后的大小
# width_i = 600
# height_i = 600
#
# # 每行每列显示图片数量
# row_max = 1
# column_max = 2
#
# # 参数初始化
# all_path = []
# num = 0
# pic_max = row_max * column_max
#
# dirName = os.getcwd()
#
# # 所有jpg图片
# for root, dirs, files in os.walk(dirName):
#     for file in files:
#         if "jpg" in file:
#             all_path.append(os.path.join(root, file))
#
# # 新建画布
# toImage = Image.new('RGBA', (600, 800))
#
# for item in all_path:
#     pic_fole_head = Image.open(item)
#     if 'qrcode.jpg' in item:
#         qtmppic = pic_fole_head.resize((200, 200))
#         qloc = (0, 600)
#         toImage.paste(qtmppic, qloc)
#     if "lingqu.jpg" in item:
#         ltmppic = pic_fole_head.resize((400, 200))
#         lloc = (200, 600)
#         toImage.paste(ltmppic, lloc)
#     if "01.jpg" in item:
#         itmppic = pic_fole_head.resize((600, 600))
#         iloc = (0, 0)
#         toImage.paste(itmppic, iloc)
#
# # for i in range(0, row_max):
# #     for j in range(0, column_max):
# #         img = all_path[num]
# #         pic_fole_head = Image.open(img)
# #         width, height = pic_fole_head.size
# #
# #         if "qrcode" in img:
# #             tmppic = pic_fole_head.resize((200, 200))
# #         else:
# #             tmppic = pic_fole_head.resize((int(width / 1), int(height / 1)))
# #
# #         loc = (int(i % row_max * width_i), int(j % column_max * height_i))
# #
# #         # print("第" + str(num) + "存放位置" + str(loc))
# #         toImage.paste(tmppic, loc)
# #         num = num + 1
# #
# #         if num >= len(all_path):
# #             print("breadk")
# #             break
# #
# #         if num >= pic_max:
# #             break
#
# print(toImage.size)
# toImage.save('merged.png')