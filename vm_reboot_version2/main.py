#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import datetime
import pymysql
import logging
import rsa
import base64
from vmreboot_client import MyClient
# from sendemail import send_email

def get_vm_list(config):
    try:
        conn = pymysql.connect(host=config["db.host"], port=3306,
                               user=config["db.username"], passwd=config["db.password"],
                               db=config["db.dbname"], charset="utf8")
        cur = conn.cursor()

        cur.execute("SELECT id,vHostIP,vPCName FROM cpsClient ORDER BY id ASC limit 30, 40")
        rowcount = cur.rowcount

        vm_list = cur.fetchall()
        # if rowcount:
        #     logging.info("从数据库中查询到{0}条记录，分别为：\n{1}".format(rowcount, vm_list))
        # else:
        #     logging.info("并未从数据库中查询到记录，没有主机需要关机")
        return vm_list
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def change_crawler_state(config, id, state):
    try:
        conn = pymysql.connect(host=config["db.host"], port=3306,
                               user=config["db.username"], passwd=config["db.password"],
                               db=config["db.dbname"], charset="utf8")
        cur = conn.cursor()
        rowcount = cur.execute("UPDATE cpsClient SET action=%s WHERE id=%s", [state, id])
        conn.commit()

        if rowcount:
            logging.info("修改id为{0}主机的状态字段成功".format(id))
        else:
            logging.error("修改id为{0}主机的状态字段失败".format(id))
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def update_reboot_time(config, id):
    try:
        conn = pymysql.connect(host=config["db.host"], port=3306,
                               user=config["db.username"], passwd=config["db.password"],
                               db=config["db.dbname"], charset="utf8")
        cur = conn.cursor()
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        rowcount = cur.execute("UPDATE cpsClient SET tLastReboot=%s WHERE id=%s", [now, id])
        conn.commit()

        if rowcount:
            logging.info("修改id为{0}主机的tLastReboot字段成功".format(id))
        else:
            logging.error("修改id为{0}主机的tLastReboot字段失败".format(id))
    finally:
        if cur:
            cur.close()
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
                config[temp_list[0].strip()] = temp_list[1].strip()
    config["db.password"] = rsa.decrypt(base64.b64decode(config["db.password"].encode("utf-8")), privkey).decode(
        "utf-8")
    config["esxi.password"] = rsa.decrypt(base64.b64decode(config["esxi.password"].encode("utf-8")), privkey).decode(
        "utf-8")
    return config


def main():
    config = read_config()
    vm_list = get_vm_list(config)
    index = 0
    vm_num = len(vm_list)
    if vm_num == 0:
        # print("没有在数据库中查询到虚拟机列表，程序即将退出")
        logging.error("没有在数据库中查询到虚拟机列表，程序即将退出")
        exit(1)
    else:
        total_time = 12 * 3600 // vm_num
        # wait_time3 = total_time - int(config["wait_time1"]) - int(config["wait_time2"])
        while True:
            time_start = time.time()
            index = index % vm_num
            # vm[0]是爬虫id，vm[1]是esxi主机ip，vm[2]虚拟机name
            vm = vm_list[index]

            # 尝试关闭虚拟机电源前，先获取其电源状态并检查是否可以连接上
            client = MyClient(vm[1], 54545, config["esxi.username"], config["esxi.password"], vm[2])
            state = client.get_power_state()
            if not state:
                logging.error("can't coonnect to ESXi host:{0}".format(vm[1]))
                wait_time3 = int(total_time-(time.time()-time_start))
                logging.info("等待{0}秒".format(wait_time3))
                time.sleep(wait_time3)
                continue
            if state == "on":
                # 首先改变爬虫状态
                change_crawler_state(config, vm[0], 1)
                # 等待一定时间让爬虫工作完
                logging.info("等待{0}秒".format(config["wait_time1"]))
                time.sleep(int(config["wait_time1"]))

                for i in list(range(10)):
                    if not client.poweroff():
                        state = client.get_power_state()
                        if "off" == state:
                            break
                        else:
                            if i == 9:
                                # send_email("无法关闭虚拟机电源，爬虫id：{0}，esxi主机ip：{1}，虚拟机name：{2}"
                                        #    .format(vm[0], vm[1], vm[2]), config["email"])
                                logging.error("无法关闭虚拟机电源，爬虫id：{0}，esxi主机ip：{1}，虚拟机name：{2}"
                                              .format(vm[0], vm[1], vm[2]) )
                                break
                            time.sleep(6)
                    else:
                        break

            # 等待一定时间后开启电源
            logging.info("等待{0}秒".format(config["wait_time2"]))
            time.sleep(int(config["wait_time2"]))
            # 尝试开启虚拟机电源
            state = client.get_power_state()
            if state == "off":
                for i in list(range(10)):
                    if not client.poweron():
                        state = client.get_power_state()
                        if "on" == state:
                            break
                        else:
                            if i == 9:
                                # send_email("无法关闭虚拟机电源，爬虫id：{0}，esxi主机ip：{1}，虚拟机name：{2}"
                                        #    .format(vm[0], vm[1], vm[2]), config["email"])
                                logging.error("无法开启虚拟机电源，爬虫id：{0}，esxi主机ip：{1}，虚拟机name：{2}"
                                              .format(vm[0], vm[1], vm[2]) )
                                break
                            time.sleep(6)
                    else:
                        break
            if "on" == client.get_power_state():
                update_reboot_time(config, vm[0])
                change_crawler_state(config, vm[0], 0)
            # 进入等待状态
            wait_time3 = int(total_time-(time.time()-time_start))
            logging.info("等待{0}秒".format(wait_time3))
            time.sleep(wait_time3)
            index += 1


if __name__ == '__main__':
    main()
