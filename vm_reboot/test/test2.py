#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim-cmd hostsvc/net/vnic_info | grep ipAddress
import time
import datetime
# import pymysql
import logging
# import rsa
import base64
import vmreboot_client
# from sendemail import send_email


def main():
    # config = read_config()
    # vm_list = get_vm_list(config)
    vm_list = []
    vm_list.append(["1", "192.168.11.249", "client CentOS6.9"])
    vm_list.append(["2", "192.168.11.249", "Sever CentOS6.9"])
    vm_list.append(["3", "192.168.11.249", "SNMP centOS6.9"])

    index = 0
    vm_num = len(vm_list)
    if vm_num == 0:
        print("没有在数据库中查询到虚拟机列表，程序即将退出")
        logging.error("没有在数据库中查询到虚拟机列表，程序即将退出")
        exit(1)
    else:
        total_time = 300 // vm_num
        # wait_time3 = total_time - int(config["wait_time1"]) - int(config["wait_time2"])
        while True:
            time_start = time.time()
            index = index % vm_num
            # vm[0]是爬虫id，vm[1]是esxi主机ip，vm[2]虚拟机name
            vm = vm_list[index]

            # 尝试关闭虚拟机电源前，先获取其电源状态并检查是否可以连接上
            client = vmreboot_client.MyClient(vm[1], 54545, "root", "1111111", vm[2])
            state = client.get_power_state()
            if not state:
                logging.error("can't coonnect to ESXi host:", vm[1])
                wait_time3 = int(total_time-(time_start-time.time()))
                print("等待{0}秒".format(wait_time3))
                time.sleep(wait_time3)
                continue
            if state == "on":
                # 首先改变爬虫状态
                #change_crawler_state(config, vm[0], 1)
                # 等待一定时间让爬虫工作完
                print("等待{0}秒".format(5))
                time.sleep(5)

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
            print("等待{0}秒".format(5))
            time.sleep(5)
            # 尝试开启虚拟机电源
            state = client.get_power_state()
            if state == "off":
                for i in list(range(10)):
                    if not client.poweroff():
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
                logging.info("改变了数据库状态：0")
                #update_reboot_time(config, vm[0])
                #change_crawler_state(config, vm[0], 0)
            # 进入等待状态
            wait_time3 = int(total_time-(time_start-time.time()))
            print("等待{0}秒".format(wait_time3))
            time.sleep(wait_time3)
            index += 1


if __name__ == '__main__':
    main()
