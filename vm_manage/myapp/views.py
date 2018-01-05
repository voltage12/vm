#!/usr/bin/python
# -*- coding: UTF-8 -*-

from myapp import application, cache
from flask import render_template
from flask import request, session, redirect, url_for
from flask import jsonify, flash, abort
from myapp import utils
from myapp import dao
from myapp.vmreboot_client import MyClient
from functools import wraps


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        username = session.get("user")
        if not username or username == "":
            return redirect(url_for("login_page"))
        return func(*args, **kwargs)
    return decorated_function


@application.route("/", methods=["POST", "GET"])
@application.route("/index", methods=["POST", "GET"])
@login_required
def index():
    username = session.get("user")
    u_id = dao.get_id_by_username(username)
    if u_id:
        permission_list = dao.list_permission_by_user(u_id)
        department_list = []
        vm_list = []
        permission_dict = {}
        power_state_dict = {}

        for permission in permission_list:
            department = dao.get_department_by_id(permission["d_id"])
            department_list.append(department)
            permission_dict[department["id"]] = permission["permission"].split(",")
            vm_list_temp = dao.list_vm_by_department(department["id"])
            vm_list = vm_list + list(vm_list_temp)

        thread_list = []
        for vm in vm_list:
            cache_key = vm["id"]
            power_state = cache.get(cache_key)
            if power_state:
                power_state_dict[cache_key] = power_state
            else:
                client_temp = MyClient(vm["host_ip"], 54545, vm["name"])
                thread_temp = utils.GetPowerStateThread(client_temp, power_state_dict, cache, vm)
                thread_temp.start()
                thread_list.append(thread_temp)
        for thread_temp in thread_list:
            thread_temp.join()

        staff_dict = {}
        for department in department_list:
            staff_list = dao.list_staff_by_department(department["id"])
            staff_dict[department["name"]] = staff_list

        return render_template("index.html", active="vm_manage",title="虚拟机管理页面",
                               department_list=department_list, staff_dict=staff_dict,
                               permission_dict=permission_dict, vm_list=vm_list,
                               power_state_dict=power_state_dict, username=username)
    else:
        abort(500)


@application.route("/loginpage")
def login_page():
    if session.get("user"):
        return redirect(url_for("index"))
    return render_template("login.html")


@application.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        flash("用户名和密码不能为空")
        return redirect(url_for("login_page"))

    md5_str = dao.get_password(username)
    if not md5_str:
        flash("此用户不存在")
        return redirect(url_for("login_page"))
    if utils.check_password(password, md5_str):
        session["user"] = username
        return redirect(url_for("index"))
    else:
        flash("用户名或密码错误")
        return redirect(url_for("login_page"))


@application.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("login_page"))


@application.route("/getstate", methods=["POST"])
def get_vm_power_state():
    v_id = request.form.get("v_id")
    data = {}
    if v_id:
        v_id = v_id.strip()
        try:
            int(v_id)
        except:
            data["result"] = "fail"
            data["errorinfo"] = "提交的虚拟机信息不正确"
        vm = dao.get_vm_by_id(int(v_id))
        client_temp = MyClient(vm["host_ip"], 54545, vm["name"])
        power_state = client_temp.get_power_state()
        if power_state:
            cache.set(vm["id"], power_state, 3600)
            data["result"] = "success"
            data["state"] = power_state
        else:
            data["result"] = "fail"
            data["errorinfo"] = "查询失败"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "没有提交需要查询的虚拟机信息"
    return jsonify(data)


@application.route("/getvmlist", methods=["POST"])
def getvmlist():
    username = session.get("user")
    if username:
        u_id = dao.get_id_by_username(username)
        if u_id:
            permission_list = dao.list_permission_by_user(u_id)
            permission_dict = {}
            for permission in permission_list:
                permission_dict[permission["d_id"]] = permission["permission"].split(",")
        else:
            abort(403)
    else:
        abort(403)
    s_id = request.form.get("s_id")
    d_id = request.form.get("d_id")
    data = {}
    vm_list = []
    power_state_dict = {}
    data["permission_dict"] = permission_dict
    if s_id:
        vm_list = dao.list_vm_by_staff(int(s_id))
        data["vm_list"] = vm_list
    elif d_id:
        vm_list = dao.list_vm_by_department(int(d_id))
        data["vm_list"] = vm_list
    thread_list = []
    for vm in vm_list:
        cache_key = vm["id"]
        power_state = cache.get(cache_key)
        if power_state:
            power_state_dict[cache_key] = power_state
        else:
            client_temp = MyClient(vm["host_ip"], 54545, vm["name"])
            thread_temp = utils.GetPowerStateThread(client_temp, power_state_dict, cache, vm)
            thread_temp.start()
            thread_list.append(thread_temp)
    for thread_temp in thread_list:
        thread_temp.join()
    data["power_state_dict"] = power_state_dict
    return jsonify(data)


@application.route("/powermanage", methods=["POST"])
def powermanage():
    username = session.get("user")
    if username:
        u_id = dao.get_id_by_username(username)
        if u_id:
            permission_list = dao.list_permission_by_user(u_id)
            permission_dict = {}
            for permission in permission_list:
                permission_dict[permission["d_id"]] = permission["permission"].split(",")
        else:
            abort(403)
    else:
        abort(403)
    v_id = request.form.get("v_id")
    action = request.form.get("action")
    data = {}
    if v_id and action:
        v_id = v_id.strip()
        action = action.strip()
        try:
            int(v_id)
        except:
            data["result"] = "fail"
            data["errorinfo"] = "提交的虚拟机信息不正确"
            return jsonify(data)
        vm = dao.get_vm_by_id(int(v_id))
        if action in permission_dict[vm["d_id"]]:
            client_temp = MyClient(vm["host_ip"], 54545, vm["name"])
            if action == "on":
                if client_temp.poweron():
                    cache.set(int(v_id), "on")
                    data["result"] = "success"
                else:
                    data["result"] = "fail"
                    data["errorinfo"] = "执行开机操作失败"
            elif action == "off":
                if client_temp.poweroff():
                    cache.set(int(v_id), "off")
                    data["result"] = "success"
                else:
                    data["result"] = "fail"
                    data["errorinfo"] = "执行关机操作失败"
            else:
                if client_temp.poweroff():
                    if client_temp.poweron():
                        data["result"] = "success"
                    else:
                        data["result"] = "fail"
                        data["errorinfo"] = "执行重启操作失败，无法成功开机"
                else:
                    data["result"] = "fail"
                    data["errorinfo"] = "执行重启操作失败，无法成功关机"
        else:
            data["result"] = "fail"
            data["errorinfo"] = "没有权限"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "没有提交需要操作的虚拟机信息"
    return jsonify(data)


@application.route("/batch_powermanage", methods=["POST"])
def batch_powermanage():
    username = session.get("user")
    if username:
        u_id = dao.get_id_by_username(username)
        if u_id:
            permission_list = dao.list_permission_by_user(u_id)
            permission_dict = {}
            for permission in permission_list:
                permission_dict[permission["d_id"]] = permission["permission"].split(",")
        else:
            abort(403)
    else:
        abort(403)

    selected_id = request.form.get("selected_id")
    action = request.form.get("action")
    data = {}
    if action and selected_id:
        selected_id = selected_id.strip()
        action = action.strip()
        id_list = selected_id.split(",")

        power_state_dict = {}
        success_list = []
        fail_list = []
        for v_id in id_list:
            if v_id == "":
                continue
            try:
                int(v_id)
            except:
                continue
            vm = dao.get_vm_by_id(int(v_id))
            if action in permission_dict[vm["d_id"]]:
                client_temp = MyClient(vm["host_ip"], 54545, vm["name"])
                if action == "on":
                    if client_temp.poweron():
                        cache.set(int(v_id), "on")
                        success_list.append(vm["name"])
                        power_state_dict[v_id] = "on"
                    else:
                        fail_list.append(vm["name"])
                elif action == "off":
                    if client_temp.poweroff():
                        cache.set(int(v_id), "off")
                        power_state_dict[v_id] = "off"
                        success_list.append(vm["name"])
                    else:
                        fail_list.append(vm["name"])
                else:
                    if client_temp.poweroff():
                        if not client_temp.poweron():
                            power_state_dict[v_id] = "off"
                            fail_list.append(vm["name"])
                        else:
                            success_list.append(vm["name"])
                    else:
                        fail_list.append(vm["name"])
            else:
                fail_list.append(vm["name"])
        data["power_state_dict"] = power_state_dict
        data["success_list"] = success_list
        data["fail_list"] = fail_list
    return jsonify(data)


