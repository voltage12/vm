#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import paramiko
import re

from paramiko import AuthenticationException

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='vmmanage_log.txt',
                filemode='w')

class VirtualMachine:
    def __init__(self):
        self.id = None
        self.name = None
        self.powerstate = None

class VmCommand:
    def __init__(self, ipadd, username, pwd, ids):
        self.ipadd = ipadd
        self.username = username
        self.pwd = pwd
        self.ids = ids

    def poweroff(self):
        try:
            s = paramiko.SSHClient()
            try:
                s.load_host_keys("host_key.txt")
            except:
                logging.error("读取host_key.txt文件失败")
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(hostname=self.ipadd, username=self.username, password=self.pwd)

            for id in self.ids:
                std_in, std_out, std_err = s.exec_command("vim-cmd vmsvc/power.off {0}".format(id))
                result_err = std_err.read().decode("utf-8").strip()
                result = std_out.read().decode("utf-8").strip()
                logging.info("ESXi主机（{2}）：执行命令 vim-cmd vmsvc/power.off {0}，结果：\n{1}".format(id, result, self.ipadd))
                if result_err != "":
                    logging.error("ESXi主机（{2}）：执行命令 vim-cmd vmsvc/power.off {0}，错误信息：{1}".format(id, result_err, self.ipadd))
        finally:
            if s:
                s.close()

    def poweron(self):
        try:
            s = paramiko.SSHClient()
            try:
                s.load_host_keys("host_key.txt")
            except:
                logging.error("读取host_key.txt文件失败")
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(hostname=self.ipadd, username=self.username, password=self.pwd)

            for id in self.ids:
                std_in, std_out, std_err = s.exec_command("vim-cmd vmsvc/power.on {0}".format(id))
                result_err = std_err.read().decode("utf-8").strip()
                result = std_out.read().decode("utf-8").strip()
                logging.info("ESXi主机（{2}）：执行命令 vim-cmd vmsvc/power.on {0}，结果：\n{1}".format(id, result, self.ipadd))
                if result_err != "":
                    logging.error("ESXi主机（{2}）：执行命令 vim-cmd vmsvc/power.on {0}，错误信息：{1}".format(id, result_err, self.ipadd))
        finally:
            if s:
                s.close()

    def getpowerstate(self):
        try:
            s = paramiko.SSHClient()
            try:
                s.load_host_keys("host_key.txt")
            except:
                logging.error("读取host_key.txt文件失败")
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(hostname=self.ipadd, username=self.username, password=self.pwd)
            result = {}
            exec_str = ""
            for id in self.ids:
                exec_str += "vim-cmd vmsvc/power.getstate {0};".format(id)

            std_in, std_out, std_err = s.exec_command(exec_str)
            lines = std_out.readlines()
            # logging.info("ESXi主机（{2}）：执行命令 vim-cmd vmsvc/power.getstate {0}，结果：\n{1}".format(id, lines[1].strip(), self.ipadd))
            index_list = list(range(0, len(self.ids)*2))
            print(index_list)
            index_list = index_list[1::2]
            print(index_list)
            for index in index_list:
                if lines[index].strip().split()[1] == "off":
                    result[self.ids[index//2]] = "off"
                else:
                    result[self.ids[index//2]] = "on"
            return result
        finally:
            if s:
                s.close()

    def getpowerstate_by_id(self, id):
        try:
            s = paramiko.SSHClient()
            try:
                s.load_host_keys("host_key.txt")
            except:
                logging.error("读取host_key.txt文件失败")
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(hostname=self.ipadd, username=self.username, password=self.pwd)
            result = {}
            std_in, std_out, std_err = s.exec_command("vim-cmd vmsvc/power.getstate {0}".format(id))
            lines = std_out.readlines()
            logging.info("ESXi主机（{2}）：获取id为{0}的虚拟机的电源状态，结果：\n{1}".format(id, lines[1].strip(), self.ipadd))
            if lines[1].strip().split()[1] == "off":
                result = "off"
            else:
                result = "on"
            return result
        finally:
            if s:
                s.close()

    def getvmlist(self):
        try:
            s = paramiko.SSHClient()
            try:
                s.load_host_keys("host_key.txt")
            except:
                logging.error("读取host_key.txt文件失败")
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(hostname=self.ipadd, username=self.username, password=self.pwd)

            std_in, std_out, std_err = s.exec_command("vim-cmd vmsvc/getallvm")
            result_err = std_err.read().decode("utf-8").strip()

            vm_list = []
            self.ids = []

            lines = std_out.readlines()
            for line in lines[1:]:
                line = line.strip()
                infos = re.split(r'\s+', line)
                vm_temp = VirtualMachine()
                vm_temp.id = infos[0]
                vm_temp.name = infos[1]
                vm_temp.powerstate = "off"
                vm_list.append(vm_temp)
                self.ids.append(infos[0])

            powerstates = self.getpowerstate()
            for vm in vm_list:
                vm.powerstate = powerstates[vm.id]

            logging.info("ESXi主机（{0}）：获取虚拟机列表".format(self.ipadd))
            if result_err != "":
                logging.error("ESXi主机（{0}）：获取虚拟机列表时出现错误，错误信息：{1}".format(self.ipadd, result_err))
            return vm_list
        finally:
            if s:
                s.close()

class VmManager:

    def __init__(self, username=None, pwd=None):
        self.ip_list = []
        self.current_ip = None
        self.vm_list = []
        self.id_list = []
        self.username = username
        self.pwd = pwd

    def read_all_ip(self):
        f = None
        self.ip_list = []
        try:
            with open("./ip.txt", "r") as f:
                for ip in f.readlines():
                    ip = ip.strip()
                    if ip[0] == "#":
                        continue
                    else:
                        self.ip_list.append(ip)
                return True
        except IOError:
            return False

    def get_all_vm(self):
        self.vm_list = []
        vmcom = VmCommand(self.current_ip, self.username, self.pwd, [])
        self.vm_list = vmcom.getvmlist()

    def check_the_pwd(self, username, pwd, ipadd):
        try:
            s = paramiko.SSHClient()
            try:
                s.load_host_keys("host_key.txt")
            except:
                logging.error("读取host_key.txt文件失败")
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(hostname=ipadd, username=username, password=pwd)
            return True
        except AuthenticationException:
            return False
