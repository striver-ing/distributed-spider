# -*- coding: utf-8 -*-
'''
Created on 2017-08-08 13:02
---------
@summary: 文本加密解密
---------
@author: Boris
'''


import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import base64

class Prpcrypt():
    def __init__(self, key):
        '''
        @summary:
        ---------
        @param key:秘钥 长度需要为16, 过长或不足自动截取或追加
        ---------
        @result:
        '''

        # 支持中文
        key = key.encode('utf8')
        key = base64.b64encode(key)
        key = key.decode('utf8')

        self.append = '\0'
        self.key = (key + (16 - len(key) % 16) * self.append)[:16]
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        #这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        cryptor = AES.new(self.key, self.mode, self.key)

        #中文加密长度有问题， 先转成英文， 这里用到base64加密。加密后的就是英文数字了。解密时先用AES解密，然后再用base64解密即可
        text = text.encode('utf8')
        text = base64.b64encode(text)
        text = text.decode('utf8')
        #加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
        text = text + (AES.block_size - (len(text) % AES.block_size)) * self.append
        self.ciphertext = cryptor.encrypt(text)
        #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        #所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext).decode('utf8')

    #解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        try:
            cryptor = AES.new(self.key, self.mode, self.key)
            plain_text = cryptor.decrypt(a2b_hex(text))
            text = plain_text.decode('utf8').rstrip('\0')
            return base64.b64decode(text).decode('utf8')
        except:
            print("秘钥不符, 解密失败")


if __name__ == '__main__':
    keys = 'pattek.com.cn'

    text = "测试"

    prpcrypt = Prpcrypt(keys) #初始化密钥
    encrypt_text = prpcrypt.encrypt(text)
    # prpcrypt = Prpcrypt('你好aa') #初始化密钥
    decrypt_text = prpcrypt.decrypt(encrypt_text)

    print(encrypt_text)
    print(decrypt_text)
