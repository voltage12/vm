#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import paramiko
import re
from os import path

from paramiko import AuthenticationException

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='vmmanage_log.txt',
                    filemode='a')


class VirtualMachine:
    def __init__(self):
        self.id = None
        self.name = None
        self.powerstate = None


class VmCommand:
    def __init__(self, ipadd, username, pwd):
        self.ipadd = ipadd
        self.username = username
        self.pwd = pwd

        self.sshclient = paramiko.SSHClient()

        if path.exists("host_key.txt"):
            self.sshclient.load_host_keys("host_key.txt")
        else:
            try:
                f = open("host_key.txt", mode="w", encoding="utf-8")
                f.write("")
                f.close()
                self.sshclient.load_host_keys("host_key.txt")
            except IOError:
                logging.error("创建host_key.txt文件失败")

        self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def power_manage(self, action, id=None, name=None):
        try:
            self.sshclient.connect(hostname=self.ipadd, username=self.username, password=self.pwd)

            if id:
                cmd_str = "vim-cmd vmsvc/power.{0} {1}".format(action, id)
                std_in, std_out, std_err = self.sshclient.exec_command(cmd_str)

                result_err = std_err.read().decode("utf-8").strip()
                result = std_out.read().decode("utf-8").strip()
                logging.info("对ESXi主机（{0}）：执行命令：\n{1}，结果：\n{2}".format(self.ipadd, cmd_str, result))
                if result_err != "":
                    logging.error("对ESXi主机（{0}）：执行命令：\n{1}，错误信息：\n{2}".format(self.ipadd, cmd_str, result_err))
            else:
                cmd_str = "vim-cmd vmsvc/getallvm | grep {0} | cut -d\" \" -f 1 | xargs -0 -n 1 vim-cmd vmsvc/power.{1}".format(
                    name, action)
                std_in, std_out, std_err = self.sshclient.exec_command(cmd_str)

                result_err = std_err.read().decode("utf-8").strip()
                result = std_out.read().decode("utf-8").strip()
                logging.info("对ESXi主机（{0}）：执行命令：\n{1}，结果：\n{2}".format(self.ipadd, cmd_str, result))
                if result_err != "":
                    logging.error("对ESXi主机（{0}）：执行命令：\n{1}，错误信息：\n{2}".format(self.ipadd, cmd_str, result_err))
        except paramiko.BadHostKeyException:
            logging.error("远程主机的hostkey验证无法通过，请清空host_key.txt中的内容")
        except paramiko.SSHException:
            logging.error("无法建立ssh连接，请保证能里连接上远程主机")
        except:
            logging.error("未知错误")
        finally:
            if self.sshclient:
                self.sshclient.close()




