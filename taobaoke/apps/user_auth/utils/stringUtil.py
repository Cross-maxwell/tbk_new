# -*- coding: utf-8 -*-

import string
import random


def random_num(length=8):
    chars = string.digits
    result = ''
    for i in range(length):
        result += random.choice(chars)
    return result