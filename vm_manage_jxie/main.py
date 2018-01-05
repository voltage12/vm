#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import pymysql
import vmcmd
import logging
import rsa
import base64

def list_vm(config):
    try:
        conn = pymysql.connect(host=config["db.host"], port=3306,
                               user=config["db.username"], passwd=config["db.password"],
                               db=config["db.dbname"])
        cur = conn.cursor()

        cur.execute("SELECT id,ip,vm_id,vm_name FROM vm_list")
        rowcount = cur.rowcount

        vm_list = []
        for row in cur:
            print(row)
            vm_list.append(row)

        if rowcount:
            logging.info("从数据库中查询到{0}条记录，分别为：\n{1}".format(rowcount, vm_list))
        else:
            logging.info("并未从数据库中查询到记录，没有主机需要关机")
        return vm_list
    finally:
        if conn:
            conn.close()

def delete_vm(config, vm_info):
    try:
        conn = pymysql.connect(host=config["db.host"], port=3306,
                               user=config["db.username"], passwd=config["db.password"],
                               db=config["db.dbname"])
        cur = conn.cursor()

        rowcount = cur.execute("delete FROM vm_list WHERE id=%s", (vm_info[0]))
        if rowcount:
            logging.info("成功从数据库中删除一条记录：\n{0}".format(vm_info))
        else:
            logging.info("从数据库中删除记录失败：\n{0}".format(vm_info))
        conn.commit()
    finally:
        if conn:
            conn.close()

def read_config():
    privkey_str = '''-----BEGIN RSA PRIVATE KEY-----
MIGrAgEAAiEAi3LrsOeD/ucd6ZMjdv6/QgICfgtx6iBqAOB0IRrApOkCAwEAAQIg
NZ9WVGtiTXWwAe5rl8lzkqoTVbBDq80lVJHGWPsiBgECEgDJu+/nICIgs9pH4Wah
Tb4dwQIQALD10oWN3h65bABq83ghKQIRBSGdqZBcrd5FSBzIooO6uUECDwbAytDn
8hMQFmwJqNLryQISAKXZj5r4SZrZxOpdqh8+n4CW
-----END RSA PRIVATE KEY-----'''
    privkey = rsa.PrivateKey.load_pkcs1(privkey_str.encode("utf-8"))
    f = open(file="app.conf", mode="r", encoding="utf-8")

    lines = f.readlines()
    config = {}
    for line in lines:
        line = line.strip()
        if line:
            if line[0] != "#":
                temp_list = line.split(":")
                config[temp_list[0]] = temp_list[1]
    config["db.password"] = rsa.decrypt(base64.b64decode(config["db.password"].encode("utf-8")),privkey).decode("utf-8")
    config["esxi.password"] = rsa.decrypt(base64.b64decode(config["esxi.password"].encode("utf-8")),privkey).decode("utf-8")
    # print(config["esxi.password"])
    return config

def read_vm_list():
    with open("vmlist.txt", encoding="utf-8") as f:
        lines = f.readlines()
        vm_list_off = []
        vm_list_on = []
        current = vm_list_off
        for line in lines:
            line = line.strip()
            if line:
                if line == "poweron:":
                    current = vm_list_on
                elif line == "poweroff:":
                    current = vm_list_off
                else:
                    current.append(line)
        return vm_list_off, vm_list_on

def main():
    vm_list_off, vm_list_on = read_vm_list()
    print(vm_list_off)
    print(vm_list_on)

if __name__ == '__main__':
    main()
    # config = read_config()
    # list_vm(config)