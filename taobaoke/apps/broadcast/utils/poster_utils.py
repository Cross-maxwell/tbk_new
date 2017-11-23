# coding=utf-8
import os
from PIL import Image
from PIL import ImageFont, ImageDraw
import datetime
import qrcode
from broadcast.utils import OSSMgr
import uuid

lines_list = [
                          [u"赚钱也是有风口的", u"而我们从事的", u"共享经济下的新零售", u"就是风口"],
                          [u"与其临渊羡鱼", u"不如退而赚钱", u"将来的你", u"定会感激", u"此刻，有远见的你"],
                          [u"每一个成功者", u"都有一个开始", u"勇于尝试", u"才能走上成功之路"],
                          [u"进过很多群", u"几天才知道", u"群能帮人省钱", u"还能自己赚钱"],
                          [u"等", u"赚完了这个星期", u"就可以", u"赚下个星期了"]
                        ]

red_text_list = [u"#让有远见的人先富起来#",
                                  u"#今天我要好好赚钱#",
                                  u"#现在开始好好赚钱#",
                                  u"#赚钱真是令人着迷#"]

# 服务器项目目录
base_path = '/home/new_taobaoke/taobaoke/apps'
# adam 本地项目目录
# base_path = '/home/adam/mydev/projects/taobaoke/taobaoke/apps'

bg_path  = os.path.join(base_path,'broadcast/statics/poster/background/')
font_path  = os.path.join(base_path,'broadcast/statics/poster/fonts/')

### todo
def generatePoster(url, lines, redtext):
    image_width = 720
    image_height = 1080
    if len(lines) > 3:
        image_height += (len(lines) - 3) * 100
    padding = 40
    truetype = os.path.join(font_path,'kaishu.ttf')

    image = Image.new('RGB', (image_width, image_height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    # use a truetype font
    font1 = ImageFont.truetype(truetype, 36)

    # 找到适合大小的字体大小
    maxLength = 0
    maxindex = 0
    for i, item in enumerate(lines):
        if len(item) > maxLength:
            maxLength = len(item)
            maxindex = i

    # 检测是否超过画布宽度，缩减字体
    maxStr = lines[maxindex]
    if len(redtext) > lines[maxindex]:
        maxStr = redtext
    font_size = 60
    font2 = ImageFont.truetype(truetype, font_size)
    max_w, max_h = draw.textsize(maxStr, font2)

    while max_w + 2 * padding > image_width:
        font_size = font_size - 1
        font2 = ImageFont.truetype(truetype, font_size)
        max_w, max_h = draw.textsize(lines[maxindex], font2)

    offset = font_size * 40 / 24
    # 红条
    draw.rectangle([0, 30, 30, 50], fill=(255, 0, 0))

    date = datetime.datetime.now().strftime("%Y/%m/%d")
    draw.text((padding, 25), u"【给" + date + u"的自己】", font=font1, fill=(0, 0, 0))
    c_height = 160
    for item in lines:
        # width1, height1= draw.textsize(line1, font2)
        draw.text((padding, c_height), item, font=font2, fill=(0, 0, 0))
        c_height += offset

    # 红字
    c_height += 50
    width1, height1 = draw.textsize(u"#", font2)
    width2, height2 = draw.textsize(redtext, font2)
    draw.text((padding, c_height), u"#", font=font2, fill=(0, 0, 0))
    draw.text((padding + width1, c_height), redtext, font=font2, fill=(255, 0, 0))
    draw.text((padding + width1 + width2, c_height), u"#", font=font2, fill=(0, 0, 0))

    # 二维码粘贴
    c_height += 70
    qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=12, border=1, )
    qr.add_data(url)
    qr.make(fit=True)
    qrImage = qr.make_image()
    qr_width = qrImage.size[0]
    # qrImage.show()
    image.paste(qrImage, (padding, c_height))
    c_height += qr_width
    # 小字
    font3 = ImageFont.truetype(truetype, 30)
    draw.text((padding + qr_width, c_height - 60), u"贫富", font=font3, fill=(0, 0, 0))
    draw.text((padding + qr_width, c_height - 30), u"只在", font=font3, fill=(0, 0, 0))
    draw.text((padding + qr_width - 60, c_height), u"一念之间", font=font3, fill=(0, 0, 0))

    # 右边一起赚

    font4 = ImageFont.truetype(truetype, 36)
    draw.text((image_width - 260, image_height - 100), u"【一起赚】", font=font4, fill=(0, 0, 0))

    draw.text((image_width - 300, image_height - 70), u"Make Money Together", font=font4, fill=(0, 0, 0))
    # 红条
    draw.rectangle([image.width - 240, image_height - 30, image_width - 120, image_height], fill=(255, 0, 0))
    filename = '{}.jpg'.format(uuid.uuid1())
    file_path = os.path.join(base_path, 'broadcast/statics/poster/', filename)
    image.save(file_path)
    oss = OSSMgr()
    oss.bucket.put_object_from_file(filename, file_path)
    return 'http://md-oss.di25.cn/{}'.format(filename)


def generatePoster_ran(url):
    import random
    line = lines_list[random.randint(0, len(lines_list) - 1)]
    red_text = red_text_list[random.randint(0, len(red_text_list) - 1)]
    return generatePoster(url, line, red_text)


if __name__ == "__main__":
    print 'test.'
    print(
        generatePoster('http://www.cnblogs.com/sfnz/', [u"“我认为", u"真正能赚钱的好项目", u'应该由我们全体老百姓来做”', u"——郎咸平"], u'比如一起赚项目'))
