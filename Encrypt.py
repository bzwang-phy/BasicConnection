#!/usr/bin/env python3

import math
import random
import struct


class ByteMap(object):
    def __init__(self, key=None):
        self.keylen = 256
        if key:
            self.key = key
        else:
            self.key = self.get_key()
        self.invkey = self.inverse_key()
        
    def get_key(self):
        lst = [i for i in range(self.keylen)]
        random.shuffle(lst)
        return(lst)
    
    def inverse_key(self):
        res = [0] * self.keylen
        for index, val in enumerate(self.key):
            res[val] = index
        return(res)
    
    def encode(self, byts):
        for index, byt in enumerate(byts):
            # byt taken from the stream is a integer number.
            byts[index] = self.key[byt]
    
    def decode(self, byts):
        for index, byt in enumerate(byts):
            byts[index] = self.invkey[byt]


class RC4(object):
    pass


