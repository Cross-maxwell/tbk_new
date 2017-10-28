# coding=utf-8
from math import floor

def cut_decimal(num_to_cut, keep_length):
    c = 10**keep_length
    num_to_cut *= c
    return floor(num_to_cut)/c