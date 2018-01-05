#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyVim.connect import SmartConnectNoSSL,SmartConnect,Disconnect
from pyVmomi import vim
from pyVmomi import vmodl
import atexit
import logging

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='vmmanage.log',
                filemode='w')

__author__ = 'jyxie'

class EsxiConnection(object):
    def __init__(self, ipaddress):
        self.ipadd = ipaddress
        self.service_instance = None
        self.vm_list = None
        self.is_connect = False
        
    def connect(self, user, password):
        try:
            self.service_instance = SmartConnect(host=self.ipadd, user=user, pwd=password)
        except vim.fault.InvalidLogin:
            logging.error("用户名或密码错误，无法登入ip为%s的ESXi主机" % self.ipadd)
            return 1
        except:
            logging.info("使用SmartConnect方法连接失败，ESXi主机没有受认证的SSL证书")
            logging.info("尝试使用SmartConnectNoSSL方法连接")
            try:
                self.service_instance = SmartConnectNoSSL(host=self.ipadd, user=user, pwd=password)
            except vim.fault.Invali  dLogin:
                logging.error("用户名或密码错误，无法登入ip为%s的ESXi主机" % self.ipadd)
                return 1

        if self.service_instance != None:
            logging.info("成功与ip地址为%s的ESXi主机建立连接" % self.ipadd)
            # 在程序关闭后关闭连接
            atexit.register(Disconnect, self.service_instance)
            self.get_all_vm(self.service_instance.RetrieveContent().rootFolder)
            self.is_connect = True
            return 0
        else:
            logging.error("由于未知错误，无法与ip地址为%s的ESXi主机建立连接" % self.ipadd)
            return 2

    def get_vm_by_ip(self, ipadd):
        return self.service_instance.content.searchIndex.FindByIp(None, ipadd, True)

    def get_vm_by_dnsname(self, dnsname):
        return self.service_instance.content.searchIndex.FindByDnsName(None, dnsname, True)

    def get_vm_by_uuid(self, uuid):
        # 第三个参数为True，只搜索虚拟机，第四个参数为True，根据Instance_UUID搜索虚拟机，而不是BIOS_UUID
        return  self.service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)

    def get_all_vm(self, start, depth=1):
        """
        从一个给定的虚拟机，虚拟应用或目录开始，递归查询出所有的虚拟机
        """
        maxdepth = 10

        if hasattr(start, "childEntity"):
          if depth > maxdepth:
             return
          childEn = start.childEntity
          for c in childEn:
             self.get_all_vm(c, depth + 1)
          return

        if hasattr(start, "vmFolder"):
            if depth > maxdepth:
                return
            childEn = start.vmFolder
            for c in childEn:
                self.get_all_vm(c, depth + 1)
            return

        if isinstance(start, vim.VirtualApp):
            childEn = start.vm
            for c in childEn:
             self.get_all_vm(c, depth + 1)
            return

        self.vm_list.append(start)

class VmManagement(object):
    def __init__(self):
        self.ip_list = []
        self.esxiconnection_list = []

    # 从文件中读取所有ip，忽略以#开头的ip，并去除ip的前后空格
    def read_all_ip(self):
        f = None
        try:
            with open("./ip.txt", "r") as f:
                for ip in f.readlines():
                    ip = ip.strip()
                    if ip[0] == "#":
                        continue
                    else:
                        self.ip_list.append(ip)
                return 0
        except IOError as e:
            return 1

    def get_esxiconn_by_ip(self, ipaddress):
        for connection in self.esxiconnection_list:
            if ipaddress == connection.ipadd:
                return connection

    def iplist_is_empty(self):
        if len(self.ip_list):
            return False
        else:
            return True

    def connect(self, user, password):
        # 为每个ip建立连接
        for ip in self.ip_list:
            esxiconnection_temp = EsxiConnection(ip)
            if esxiconnection_temp.connect(user, password) == 1:
                return 1
            self.esxiconnection_list.append(esxiconnection_temp)
        return 0

    def get_vm_by_ip(self, ipadd):
        for connection in self.esxiconnection_list:
            vm_temp = connection.get_vm_by_ip(ipadd)
            if vm_temp:
                return vm_temp

    def get_vm_by_dnsname(self, dnsname):
        for connection in self.esxiconnection_list:
            vm_temp = connection.get_vm_by_dnsname(dnsname)
            if vm_temp:
                return vm_temp

    def get_vm_by_uuid(self, uuid):
        # 第三个参数为True，只搜索虚拟机，第四个参数为True，根据Instance_UUID搜索虚拟机，而不是BIOS_UUID
        for connection in self.esxiconnection_list:
            vm_temp = connection.get_vm_by_uuid(uuid)
            if vm_temp:
                return vm_temp

    def get_power_state(self, vm):
        return vm.summary.runtime.powerState

    def get_name(self, vm):
        return vm.summary.config.name

    def get_instance_uuid(self, vm):
        return vm.summary.config.instanceUuid

    def get_guest_ip(self, vm):
        if vm.summary.guest != None:
            ip = vm.summary.guest.ipAddress
            if ip != None and ip != "":
                return ip
        else:
            return "None"

    def wait_for_tasks(self, service_instance, tasks):
        property_collector = service_instance.content.propertyCollector
        task_list = [str(task) for task in tasks]
        # Create filter
        obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                     for task in tasks]
        property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                                   pathSet=[],
                                                                   all=True)
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = obj_specs
        filter_spec.propSet = [property_spec]
        pcfilter = property_collector.CreateFilter(filter_spec, True)
        try:
            version, state = None, None
            while len(task_list):
                update = property_collector.WaitForUpdates(version)
                for filter_set in update.filterSet:
                    for obj_set in filter_set.objectSet:
                        task = obj_set.obj
                        for change in obj_set.changeSet:
                            if change.name == 'info':
                                state = change.val.state
                            elif change.name == 'info.state':
                                state = change.val
                            else:
                                continue

                            if not str(task) in task_list:
                                continue

                            if state == vim.TaskInfo.State.success:
                                task_list.remove(str(task))
                            elif state == vim.TaskInfo.State.error:
                                raise task.info.error
                version = update.version
        finally:
            if pcfilter:
                pcfilter.Destroy()

    def poweron_vm(self, vm, service_instance):
        if self.get_power_state(vm) == vim.HostSystem.PowerState.poweredOn:
            return True
        task = vm.PowerOnVM_Task()
        try:
            self.wait_for_tasks(service_instance, [task])
        except task.info.error:
            return False
        if self.get_power_state(vm) != vim.HostSystem.PowerState.poweredOn:
            return False
        else:
            return True

    def poweroff_vm(self, vm, service_instance):
        if self.get_power_state(vm) == vim.HostSystem.PowerState.poweredOff:
            return True
        task = vm.PowerOffVM_Task()
        try:
            self.wait_for_tasks(service_instance, [task])
        except task.info.error:
            return False
        if self.get_power_state(vm) != vim.HostSystem.PowerState.poweredOff:
            return False
        else:
            return True

