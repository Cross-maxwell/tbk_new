# -*- coding: utf-8 -*-

from broadcast.utils import OSSMgr
from PIL import Image
import os
import uuid


all_path = []
dirName = os.getcwd()


for root, dirs, files in os.walk(dirName):
    for file in files:
        if "jpeg" in file:
            image = Image.open(file)
            new_image = image.convert("RGBA").tobytes("jpeg", "RGBA")
            filename = '{}.jpeg'.format(uuid.uuid1())
            oss = OSSMgr()
            oss.bucket.put_object(filename, new_image)
            print 'http://md-oss.di25.cn/{}?x-oss-process=image/quality,q_65'.format(filename)


