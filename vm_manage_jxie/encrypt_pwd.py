#!/usr/bin/python
# -*- coding: UTF-8 -*-
import rsa
import base64
import getpass

pubkey_str = '''-----BEGIN RSA PUBLIC KEY-----
MCgCIQCLcuuw54P+5x3pkyN2/r9CAgJ+C3HqIGoA4HQhGsCk6QIDAQAB
-----END RSA PUBLIC KEY-----'''

pubkey = rsa.PublicKey.load_pkcs1(pubkey_str.encode("utf-8"))

while True:
    pwd = getpass.getpass("请输入密码：")

    # 公钥加密
    crypto = rsa.encrypt(pwd.encode(), pubkey)
    temp = base64.b64encode(crypto)
    print("加密后的密码为：{0}".format(temp.decode("utf-8")))
