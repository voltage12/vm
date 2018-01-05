#!/usr/bin/python
# -*- coding: UTF-8 -*-

import tkinter as tk
import tkinter.messagebox as messagebox
from vm_manage import VmManager, VmCommand
import threading

def run_the_task(ipadd, username, pwd, ids, task):
    vmcom = VmCommand(ipadd, username, pwd, ids)
    if task == "on":
        vmcom.poweron()

    if task == "off":
        vmcom.poweroff()

def click_connect_bt():
    global myapp
    if myapp.vm_manager:
        myapp.vm_manager.read_all_ip()
        if myapp.vm_manager.ip_list:
            username = myapp.entry_username.get()
            pwd = myapp.entry_pwd.get()
            # messagebox.showinfo("xxx", "%s %s" % (username,pwd))
            if not myapp.vm_manager.check_the_pwd(username, pwd, myapp.vm_manager.ip_list[0]):
                messagebox.showerror("vm_manage", "用户名或密码错误")
                return

            myapp.vm_manager.username = username
            myapp.vm_manager.pwd = pwd

            # myapp.entry_username.set("")
            # myapp.entry_pwd.set("")

            myapp.listbox_ip.delete(0, myapp.listbox_ip.size()-1)
            for ip in myapp.vm_manager.ip_list:
                myapp.listbox_ip.insert(tk.END, ip)
        else:
            messagebox.showwarning("vm_manage", "请在ip.txt中输入IP地址")

def select_ip(event):
    listbox_ip = event.widget
    myapp = listbox_ip.master
    list_box_vm = myapp.list_box_vm
    vm_manager = myapp.vm_manager
    if len(listbox_ip.curselection()) != 0:
        ip = listbox_ip.get(listbox_ip.curselection()[0])
        vm_manager.current_ip = ip
        vm_manager.get_all_vm()
        vm_list = vm_manager.vm_list
        list_box_vm.delete(0, list_box_vm.size()-1)
        vm_manager.id_list = []
        for vm in vm_list:
            list_box_vm.insert(tk.END, "ID：%s  Name：%s  电源：%s" % (vm.id, vm.name, vm.powerstate))
            # list_box_vm.insert(tk.END, "ID：%-6s    Name：%s" % (vm.id, vm.name))
            vm_manager.id_list.append(vm.id)

def poweron(event):
    button = event.widget
    master = button.master
    list_box_vm = master.list_box_vm
    if len(list_box_vm.curselection()) != 0:
        ids = []
        for index in list_box_vm.curselection():
            ids.append(master.vm_manager.id_list[int(index)])
        t = threading.Thread(target=run_the_task, args=(master.vm_manager.current_ip,master.vm_manager.username,master.vm_manager.pwd,ids,"on"))
        t.start()
    else:
        messagebox.showwarning("vm_manage", "请选择要开机的虚拟机")

def poweroff(event):
    button = event.widget
    master = button.master
    list_box_vm = master.list_box_vm
    if len(list_box_vm.curselection()) != 0:
        ids = []
        for index in list_box_vm.curselection():
            ids.append(master.vm_manager.id_list[int(index)])

        t = threading.Thread(target=run_the_task,args=(master.vm_manager.current_ip, master.vm_manager.username, master.vm_manager.pwd, ids, "off"))
        t.start()
    else:
        messagebox.showwarning("vm_manage", "请选择要关机的虚拟机")

class MyApp(tk.Frame):
    def __init__(self, master, width=480, height=500):
        super().__init__(master=master, width=width, height=height)
        self.pack()
        root = self

        # 创建子控件并设置属性
        self.label_ip = tk.Label(master=root, padx=0, pady=0, text="ESXi主机IP地址列表")
        self.label_ip.place(x=10, y=10, width=150, height=20)

        self.listbox_ip = tk.Listbox(master=root, height=15, width=150)
        self.listbox_ip.place(x=10, y=30, width=150)
        self.listbox_ip.bind("<Double-Button-1>", select_ip)

        self.label_username = tk.Label(master=root, padx=0, pady=0, text="用户名")
        self.label_username.place(x=10, y=310, width=40, height=20)

        self.entry_username = tk.Entry(master=root)
        self.entry_username.place(x=55, y=310, width=105, height=20)

        self.label_pwd = tk.Label(master=root, padx=0, pady=0, text="密码")
        self.label_pwd.place(x=10, y=340, width=40, height=20)

        self.entry_pwd = tk.Entry(master=root, show="*")
        self.entry_pwd.place(x=55, y=340, width=105, height=20)

        self.button_connect = tk.Button(master=root, text="连接", command=click_connect_bt)
        self.button_connect.place(x=60, y=370, width=50, height=20)

        self.label_vmlist = tk.Label(master=root, padx=0, pady=0, text="虚拟机列表")
        self.label_vmlist.place(x=170, y=10, width=300, height=20)

        self.list_box_vm = tk.Listbox(master=root, height=25, selectmode=tk.EXTENDED)
        self.list_box_vm.place(x=170, y=30, width=300)

        self.button_poweroff = tk.Button(master=root, text="关机")
        self.button_poweroff.place(x=50, y=460, width=50, height=20)
        self.button_poweroff.bind("<ButtonRelease-1>", poweroff)

        self.button_poweron = tk.Button(master=root, text="开机")
        self.button_poweron.place(x=110, y=460, width=50, height=20)
        self.button_poweron.bind("<ButtonRelease-1>",poweron)

        self.vm_manager = VmManager()

root = tk.Tk()
root.resizable(height=False, width=False)
myapp = MyApp(master=root)
tk.mainloop()

