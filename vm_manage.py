#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyVim.connect import SmartConnectNoSSL,SmartConnect,Disconnect
from pyVmomi import vim
from pyVmomi import vmodl
import atexit
import getpass


__author__ = 'jyxie'

# 从文件中读取所有ip，忽略以#开头的ip，并去除ip的前后空格
def read_all_ip():
    f = None
    ip_list = []
    try:
        with open("./ip.txt","r") as f:
            for ip in f.readlines():
                ip = ip.strip()
                if ip[0] == "#":
                    continue
                else:
                    ip_list.append(ip)
            return ip_list
    except IOError as e:
        print("文件不存在，请在同目录下建立'ip.txt'文件并在其中输入ip地址")
        print("程序即将退出")
        exit(1)

# 建立连接，获得一个ServiceInstance对象
def get_service_instance(ipadd, user, password):
    print("")
    service_instance = None
    try:
        service_instance = SmartConnect(host=ipadd, user=user, pwd=password)
    except:
        print("尝试使用SmartConnectNoSSL方法连接")
        service_instance = SmartConnectNoSSL(host=ipadd, user=user, pwd=password)

    if service_instance != None:
        print("成功与ip地址为%s的服务器建立连接" % ipadd)
        # 在程序关闭后关闭连接
        atexit.register(Disconnect, service_instance)
    else:
        print("无法与ip地址为%s的服务器建立连接" % ipadd)
    return service_instance

def get_all_vm_simple(datacenter):
    return datacenter.vmFolder.childEntity

def get_all_vm(start, result=[], depth=1):
    """
    从一个给定的虚拟机，虚拟应用或目录开始，递归查询出所有的虚拟机
    """
    maxdepth = 10

    if hasattr(start, 'childEntity'):
      if depth > maxdepth:
         return
      vmList = start.childEntity
      for c in vmList:
         get_all_vm(c, result, depth + 1)
      return

    if isinstance(start, vim.VirtualApp):
      vmList = start.vm
      for c in vmList:
         get_all_vm(c, result, depth + 1)
      return

    result.append(start)

def print_vm_info(vm):
    summary = vm.summary
    print("虚拟机名     :", summary.config.name)
    print("UUID        :", summary.config.instanceUuid)
    # print("Path       : ", summary.config.vmPathName)
    # print("操作系统     :", summary.config.guestFullName)
    # annotation = summary.config.annotation
    # if annotation != None and annotation != "":
    #     print("注释      :", annotation)
    print("电源状态     :", summary.runtime.powerState)
    if summary.guest != None:
        ip = summary.guest.ipAddress
        if ip != None and ip != "":
            print("IP         :", ip)
    # if summary.runtime.question != None:
    #     print("Question  :", summary.runtime.question.text)

def print_all_vm_info(vm_list):
    index = 1
    print("一共有%d台虚拟机" % len(vm_list))
    for vm in vm_list:
        print("")
        print("序号", index)
        print_vm_info(vm)
        index += 1

def get_vm_by_ip(ipadd, service_instance):
    return service_instance.content.searchIndex.FindByIp(None, ipadd, True)

def get_vm_by_dnsname(dnsname, service_instance):
    return service_instance.content.searchIndex.FindByDnsName(None, dnsname, True)

def get_vm_by_uuid(uuid, service_instance):
    return  service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)

def get_vm_by_num(num, vm_list_list):
    num -= 1
    if num < 0:
        return None
    for vm_list in vm_list_list:
        if num > len(vm_list):
            num -= len(vm_list)
            continue
        else:
            return vm_list[num]
    return None

def wait_for_tasks(service_instance, tasks):
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

def get_power_state(vm):
    return vm.summary.runtime.powerState

def poweron_vm(vm, service_instance):
    if get_power_state(vm) == vim.HostSystem.PowerState.poweredOn:
        return True
    task = vm.PowerOnVM_Task()
    try:
        wait_for_tasks(service_instance, [task])
    except task.info.error:
        return False
    if get_power_state(vm) != vim.HostSystem.PowerState.poweredOn:
        return False
    else:
        return True

def poweroff_vm(vm, service_instance):
    if get_power_state(vm) == vim.HostSystem.PowerState.poweredOff:
        return True
    task = vm.PowerOffVM_Task()
    try:
        wait_for_tasks(service_instance, [task])
    except task.info.error:
        return False
    if get_power_state(vm) != vim.HostSystem.PowerState.poweredOff:
        return False
    else:
        return True

def manage(ip_num, dict_for_si, dict_for_vmlist, ip_list):
    ip = ip_list[ip_num - 1]
    service_instance = dict_for_si[ip]
    vm_list = dict_for_vmlist[ip]
    print("")
    print("对ESXi主机（IP:%s）进行管理，此主机下一共有%d台虚拟机" % (ip,len(vm_list)))
    select_num = -1
    while select_num != 0:
        print("0. 返回到上一层")
        print("1. 输出虚拟机列表")
        print("2. 根据序号开启虚拟机电源")
        print("3. 根据序号关闭虚拟机电源")
        print("4. 根据序号区间开启虚拟机电源")
        print("5. 根据序号区间关闭虚拟机电源")
        print("6. 开启所有虚拟机电源")
        print("7. 关闭所有虚拟机电源")
        select_str = input("请输入选择：")
        try:
            select_num = int(select_str)
        except:
            print("%s不是一个有效的输入" % select_str)
            select_num = -1
            continue

        if select_num == 0:
            return None
        elif select_num == 1:
            print_all_vm_info(vm_list)
        elif select_num == 2:
            nums = input("请输入序号（可输入多个，用空格隔开）：")
            nums = nums.strip()
            num_list = nums.split()
            for num_str in num_list:
                try:
                    num = int(num_str)
                    if num < 1 or num > len(vm_list):
                        print("%d不在序号范围内" % num)
                        continue
                    vm_temp = vm_list[num - 1]
                    if poweron_vm(vm_temp, service_instance):
                        print("成功开启序号为 %d 的虚拟机电源" % num)
                    else:
                        print("无法开启序号为 %d 的虚拟机电源" % num)
                except ValueError:
                    print("%s不是一个序号" % num_str)
                    continue
        elif select_num == 3:
            nums = input("请输入序号（可输入多个，用空格隔开）：")
            nums = nums.strip()
            num_list = nums.split()
            for num_str in num_list:
                try:
                    num = int(num_str)
                    if num < 1 or num > len(vm_list):
                        print("%d不在序号范围内" % num)
                        continue
                    vm_temp = vm_list[num - 1]
                    if poweroff_vm(vm_temp, service_instance):
                        print("成功关闭序号为 %d 的虚拟机电源" % num)
                    else:
                        print("无法关闭序号为 %d 的虚拟机电源" % num)
                except ValueError:
                    print("%s不是一个序号" % num_str)
                    continue
        elif select_num == 4:
            nums = input("请输入开始序号和结束序号，用空格隔开：")
            nums = nums.strip()
            num_list = nums.split()
            start_num = 0
            end_num = 0

            try:
                start_num = int(num_list[0])
                end_num = int(num_list[1])
            except:
                print("%s不是一组有效的输入" % nums)
                continue

            num_list = list(range(start_num, end_num + 1))
            for num_str in num_list:
                try:
                    num = int(num_str)
                    if num < 1 or num > len(vm_list):
                        print("%d不是一个有效的输入" % num)
                        continue
                    vm_temp = vm_list[num - 1]
                    if poweron_vm(vm_temp, service_instance):
                        print("成功开启序号为 %d 的虚拟机电源" % num)
                    else:
                        print("无法开启序号为 %d 的虚拟机电源" % num)
                except ValueError:
                    print("%s不是一个有效输入" % num_str)
                    continue
                except Exception as e:
                    print(e)
        elif select_num == 5:
            nums = input("请输入开始序号和结束序号，用空格隔开：")
            nums = nums.strip()
            num_list = nums.split()
            start_num = 0
            end_num = 0
            try:
                start_num = int(num_list[0])
                end_num = int(num_list[1])
            except:
                print("%s不是一组有效的输入" % nums)
                continue
            num_list = list(range(start_num,end_num+1))
            for num_str in num_list:
                try:
                    num = int(num_str)
                    if num < 1 or num > len(vm_list):
                        print("%d不是一个有效的输入" % num)
                        continue
                    vm_temp = vm_list[num - 1]
                    if poweroff_vm(vm_temp, service_instance):
                        print("成功关闭序号为 %d 的虚拟机电源" % num)
                    else:
                        print("无法关闭序号为 %d 的虚拟机电源" % num)
                except ValueError:
                    print("%s不是一个有效输入" % num_str)
                    continue
                except Exception as e:
                    print(e)
        elif select_num == 6:
            order_num = 1
            for vm_temp in vm_list:
                if poweron_vm(vm_temp, service_instance):
                    print("成功开启序号为 %d 的虚拟机电源" % order_num)
                else:
                    print("无法开启序号为 %d 的虚拟机电源" % order_num)
                order_num += 1
        elif select_num == 7:
            order_num = 1
            for vm_temp in vm_list:
                if poweroff_vm(vm_temp, service_instance):
                    print("成功关闭序号为 %d 的虚拟机电源" % order_num)
                else:
                    print("无法关闭序号为 %d 的虚拟机电源" % order_num)
                order_num += 1
        else:
            print("不是一个有效输入")
# 主函数
def main():
    #用于存放经过处理，并且已经连接上的IP地址
    ip_list = []
    #IP地址作为key，value是与这个IP对应的service_instance
    dict_for_si = {}
    #IP地址作为key，value是与这个IP对应的虚拟机列表
    dict_for_vmlist = {}

    user_pwd_are_ritht = False
    user = None
    password = None
    # 为每个ip建立连接
    for ip in read_all_ip():
        ip = ip.strip()
        service_instance_temp = None
        while service_instance_temp == None:
            if user_pwd_are_ritht:
                service_instance_temp = get_service_instance(ip,user,password)
                if service_instance_temp:
                    ip_list.append(ip)
                    dict_for_si[ip] = service_instance_temp
                    content = service_instance_temp.RetrieveContent()
                    datacenter_temp = content.rootFolder.childEntity[0]
                    # vm_list_temp是一个虚拟机列表
                    vm_list_temp = get_all_vm_simple(datacenter_temp)
                    dict_for_vmlist[ip] = vm_list_temp
                else:
                    print("无法建立连接，程序即将退出")
                    exit(1)
            else:
                while True:
                    user = input("请输入用户名：")
                    # password = getpass.getpass(prompt="请输入密码：")
                    password = input("请输入密码：")
                    try:
                        service_instance_temp = get_service_instance(ip, user, password)
                        if service_instance_temp:
                            user_pwd_are_ritht = True
                            ip_list.append(ip)
                            dict_for_si[ip] = service_instance_temp
                            content = service_instance_temp.RetrieveContent()
                            datacenter_temp = content.rootFolder.childEntity[0]
                            # vm_list_temp是一个虚拟机列表
                            vm_list_temp = get_all_vm_simple(datacenter_temp)
                            dict_for_vmlist[ip] = vm_list_temp
                            break
                        else:
                            print("无法建立连接，程序即将退出")
                            exit(1)
                    except vim.fault.InvalidLogin:
                        print("用户名或密码错误，请重试")
                        continue

    if len(ip_list) == 0:
        input("请在ip.txt中输入ip地址")
        exit(0)

    select_num = -1
    while select_num != 0:
        print("")
        print("0. 退出程序")
        order_num = 1
        for ip in ip_list:
            print("%d. 对ESXi主机（IP:%s）进行管理" %(order_num, ip))
            order_num += 1

        select_str = input("请输入选择：")
        try:
            select_num = int(select_str)
        except:
            print("%s不是一个有效的输入" % select_str)
            select_num = -1
            continue
        if select_num == 0:
            exit(0)
        else:
            if select_num < 1 or select_num > len(ip_list):
                print("%s不是一个有效的输入" % select_str)
                continue
            else:
                manage(select_num, dict_for_si, dict_for_vmlist, ip_list)
    return 0

# 程序入口
if __name__ == "__main__":
   main()
