#!/usr/bin/python
# -*- coding: UTF-8 -*-
import tkinter as tk


root = tk.Tk()
root.resizable(height=False, width=False)

frame_main = tk.Frame(master=root,width=480, height=500)
frame_main.pack()

label_ip = tk.Label(master=root, padx=0, pady=0, text="ESXi主机IP地址列表")
label_ip.place(x=10, y=10, width=150, height=20)

ip_list_str = tk.StringVar()

listbox_ip = tk.Listbox(master=root, height=15, width=150)
listbox_ip.place(x=10, y=30, width=150)

button_connect = tk.Button(master=root, text="连接")
button_connect.place(x=60, y=310, width=50, height=20)

label_vmlist = tk.Label(master=root, padx=0, pady=0, text="虚拟机列表")
label_vmlist.place(x=170, y=10, width=300, height=20)

list_box_vm = tk.Listbox(master=root, height=20, selectmode=tk.EXTENDED)
list_box_vm.place(x=170,y=30,width=300)

button_poweroff = tk.Button(master=root, text="关机")
button_poweroff.place(x=255, y=400, width=50, height=20)

button_poweron = tk.Button(master=root, text="开机")
button_poweron.place(x=315, y=400, width=50, height=20)

tk.mainloop()

