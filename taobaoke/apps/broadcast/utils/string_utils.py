import random
import string

def random_num(length=8):
    chars = string.digits
    result = ''
    for i in range(length):
        result += random.choice(chars)
    return result

def random_str(length=8):
    chars = string.ascii_letters + string.digits
    result = ''
    for i in range(length):
        result += random.choice(chars)
    return result