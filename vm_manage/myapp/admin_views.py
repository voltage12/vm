#!/usr/bin/python
# -*- coding: UTF-8 -*-

from myapp import application
from flask import render_template
from flask import request, session, redirect, url_for
from flask import jsonify, flash, abort
from myapp import utils
from myapp import dao
from myapp.views import login_required


@application.route("/admin/vm_manage_page")
@login_required
def vm_manage_page():
    username = session.get("user")
    if username != "root":
        abort(403)
    else:
        department_list = dao.list_department()
        active2 = {"6": "active"}
        return render_template("vm_manage.html", active="admin", title="管理页面",
                               active2=active2, username=username, department_list=department_list)


@application.route("/admin/get_vm_list", methods=["POST"])
@login_required
def get_vm_list():
    data = {}
    d_id = request.form.get("d_id")
    if d_id:
        username = session.get("user")
        u_id = dao.get_id_by_username(username)
        if u_id:
            permission_list = dao.list_permission_by_user(u_id)
            for permission in permission_list:
                if permission["d_id"] == int(d_id):
                    vm_list = dao.list_vm_by_department(int(d_id))
                    department_list = dao.list_department()
                    department_dict = {}
                    for department in department_list:
                        department_dict[department["id"]] = department["name"]
                    staff_list = dao.list_staff()
                    staff_list_temp = []
                    staff_dict = {}
                    for staff in staff_list:
                        staff_dict[staff["id"]] = staff["name"]
                        if staff["d_id"] == int(d_id):
                            staff_list_temp.append(staff)
                    data["vm_list"] = vm_list
                    data["department_dict"] = department_dict
                    data["staff_dict"] = staff_dict
                    data["staff_list"] = staff_list_temp
    return jsonify(data)


@application.route("/admin/delete_vm", methods=["POST"])
@login_required
def delete_vm():
    data = {}
    username = session.get("user")
    if username != "root":
        data["result"] = "fail"
        data["errorinfo"] = "权限不足"
        return jsonify(data)
    v_id = request.form.get("v_id")
    if v_id:
        try:
            int(v_id)
        except:
            data["result"] = "fail"
            data["errorinfo"] = "参数不正确"
            return jsonify(data)
        rowcount = dao.remove_vm_by_id(int(v_id))
        if rowcount == 0 or rowcount == None:
            data["result"] = "fail"
            data["errorinfo"] = "从数据库中删除失败"
        else:
            data["result"] = "success"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "参数不全"
    return jsonify(data)


@application.route("/admin/add_vm", methods=["POST"])
@login_required
def add_vm():
    data = {}
    username = session.get("user")
    if username != "root":
        data["result"] = "fail"
        data["errorinfo"] = "权限不足"
        return jsonify(data)
    host_ip = request.form.get("host_ip")
    name = request.form.get("name")
    s_id = request.form.get("s_id")
    d_id = request.form.get("d_id")
    if host_ip and d_id and name and s_id:
        try:
            int(d_id)
            int(s_id)
        except:
            data["result"] = "fail"
            data["errorinfo"] = "参数不正确"
            return jsonify(data)
        rowcount = dao.save_vm(host_ip, name, int(d_id), int(s_id))
        if rowcount == 0 or rowcount == None:
            data["result"] = "fail"
            data["errorinfo"] = "数据库中添加失败"
        else:
            data["result"] = "success"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "参数不全"
    return jsonify(data)


@application.route("/admin/update_vm", methods=["POST"])
@login_required
def update_vm():
    data = {}
    username = session.get("user")
    if username != "root":
        data["result"] = "fail"
        data["errorinfo"] = "权限不足"
        return jsonify(data)
    s_id = request.form.get("s_id")
    v_name = request.form.get("v_name")
    v_id = request.form.get("v_id")
    host_ip = request.form.get("host_ip")
    d_id = request.form.get("d_id")
    if s_id and v_name and d_id and v_id and host_ip:
        try:
            int(s_id)
            int(d_id)
            int(v_id)
        except:
            data["result"] = "fail"
            data["errorinfo"] = "参数不正确"
            return jsonify(data)
        rowcount = dao.update_vm(int(v_id), host_ip, v_name, int(d_id), int(s_id))
        if rowcount == 0:
            data["result"] = "fail"
            data["errorinfo"] = "数据库中更新失败"
        else:
            data["result"] = "success"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "参数不全"
    return jsonify(data)


@application.route("/admin/check_username", methods=["POST"])
def check_username():
    username = request.form.get("username")
    data = {}
    if not username or username == "":
        data["result"] = "fail"
    else:
        if dao.get_id_by_username(username) == None:
            data["result"] = "success"
            data["exist"] = "no"
        else:
            data["result"] = "success"
            data["exist"] = "yes"
    return jsonify(data)


@application.route("/admin")
@login_required
def admin():
    username = session.get("user")
    active2 = {}
    return render_template("admin.html", active="admin", title="管理页面", username=username, active2=active2)


@application.route("/admin/change_passwd_page")
@login_required
def change_passwd_page():
    username = session.get("user")
    active2 = {"2": "active"}
    return render_template("change_passwd.html", active="admin", title="管理页面", active2=active2, username=username)


@application.route("/admin/change_passwd", methods=["POST"])
@login_required
def change_password():
    username = request.form.get("username")
    password = request.form.get("password")
    new_password = request.form.get("new_password")
    data = {}
    if username and password and new_password:
        current_user = session.get("user")
        if current_user != "root" and current_user != username:
            data["result"] = "fail"
            data["errorinfo"] = "没有权限"
        else:
            if current_user != "root":
                md5_str = dao.get_password(username)
                new_md5_str = utils.get_md5(new_password)
                if not md5_str:
                    data["result"] = "fail"
                    data["errorinfo"] = "此用户不存在"
                elif not utils.check_password(password, md5_str):
                    data["result"] = "fail"
                    data["errorinfo"] = "密码错误"
                elif md5_str == new_md5_str:
                    data["result"] = "fail"
                    data["errorinfo"] = "密码与原先一致"
                else:
                    result = dao.update_password(username, new_md5_str)
                    if result == 1:
                        data["result"] = "success"
                    else:
                        data["result"] = "fail"
                        data["errorinfo"] = "修改未成功"
            else:
                md5_str = dao.get_password(username)
                new_md5_str = utils.get_md5(new_password)
                if not md5_str:
                    data["result"] = "fail"
                    data["errorinfo"] = "此用户不存在"
                else:
                    result = dao.update_password(username, new_md5_str)
                    if result == 1:
                        data["result"] = "success"
                    else:
                        data["result"] = "fail"
                        data["errorinfo"] = "修改未成功"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "用户名或密码不能为空"
    return jsonify(data)


@application.route("/admin/add_user_page")
@login_required
def add_user_page():
    username = session.get("user")
    if username != "root":
        abort(403)
    else:
        active2 = {"1": "active"}
        department_list = dao.list_department()
        if not department_list:
            department_list = []
        return render_template("add_user.html", active="admin", title="管理页面",
                               active2=active2, username=username, department_list=department_list)


@application.route("/admin/add_user", methods=["POST"])
@login_required
def add_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    permission_dict = data.get("permission_dict")
    data = {}
    if username and password and permission_dict:
        current_user = session.get("user")
        if current_user != "root":
            data["result"] = "fail"
            data["errorinfo"] = "没有权限"
        else:
            password_md5_str = utils.get_md5(password)
            result = dao.save_user(username, password_md5_str)
            if result == 1:
                u_id = dao.get_id_by_username(username)
                if u_id:
                    total_num = len(permission_dict)
                    for k, v in permission_dict.items():
                        total_num -= dao.sava_permission(u_id, int(k), v)
                    if total_num != 0:
                        data["result"] = "fail"
                        data["errorinfo"] = "添加用户成功，但在添加权限时失败，请在修改权限页面重新添加权限"
                    else:
                        data["result"] = "success"
                else:
                    abort(500)
            else:
                data["result"] = "fail"
                data["errorinfo"] = "写入数据库时失败"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "提交的信息不完整"
    return jsonify(data)


@application.route("/admin/change_permission_page", methods=["POST", "GET"])
@login_required
def change_permission_page():
    username = session.get("user")
    if username != "root":
        abort(403)
    else:
        active2 = {"3": "active"}
        department_list = dao.list_department()
        user_list = dao.list_user()
        if not user_list:
            abort(500)
        if not department_list:
            department_list = []
        return render_template("change_permission.html", active="admin", title="管理页面", user_list=user_list,
                               active2=active2, username=username, department_list=department_list)


@application.route("/admin/change_permission", methods=["POST"])
@login_required
def change_permission():
    data = request.get_json()
    u_id = data.get("u_id")
    permission_dict = data.get("permission_dict")
    data = {}
    if u_id and permission_dict:
        current_user = session.get("user")
        if current_user != "root":
            data["result"] = "fail"
            data["errorinfo"] = "没有权限"
        else:
            if dao.remove_permission_by_user(int(u_id)) == None:
                data["result"] = "fail"
                data["errorinfo"] = "操作数据库时出错"
            else:
                total_num = len(permission_dict)
                for k, v in permission_dict.items():
                    total_num -= dao.sava_permission(u_id, int(k), v)
                if total_num != 0:
                    data["result"] = "fail"
                    data["errorinfo"] = "操作数据库时出错，请在修改权限页面重新添加权限"
                else:
                    data["result"] = "success"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "提交的信息不完整"
    return jsonify(data)


@application.route("/admin/department_manage_page")
@login_required
def department_manage_page():
    username = session.get("user")
    if username != "root":
        abort(403)
    else:
        department_list = dao.list_department()
        active2 = {"4":"active"}
        return render_template("department_manage.html", active="admin", title="管理页面",
                               active2=active2, username=username, department_list=department_list)


@application.route("/admin/delete_department", methods=["POST"])
@login_required
def delete_department():
    username = session.get("user")
    data = {}
    if username != "root":
        data["result"] = "fail"
        data["errorinfo"] = "权限不足"
    else:
        d_id = request.form.get("d_id")
        if d_id:
            try:
                int(d_id)
            except:
                data["result"] = "fail"
                data["errorinfo"] = "提交的信息有误"
                return jsonify(data)
            if dao.remove_vm_by_department(int(d_id)) == None:
                data["result"] = "fail"
                data["errorinfo"] = "删除此部门下的虚拟机时出错"
            else:
                if dao.remove_staff_by_department(int(d_id)) == None:
                    data["result"] = "fail"
                    data["errorinfo"] = "删除此部门下的员工时出错"
                else:
                    if dao.remove_department(int(d_id)) == None:
                        data["result"] = "fail"
                        data["errorinfo"] = "从数据库删除部门信息出错"
                    else:
                        data["result"] = "success"
        else:
            data["result"] = "fail"
            data["errorinfo"] = "提交的信息不完整"
    return jsonify(data)


@application.route("/admin/add_department", methods=["POST"])
@login_required
def add_department():
    username = session.get("user")
    data = {}
    if username != "root":
        data["result"] = "fail"
        data["errorinfo"] = "权限不足"
    else:
        department_name = request.form.get("department_name")
        if department_name:
            if dao.save_department(department_name) == None:
                data["result"] = "fail"
                data["errorinfo"] = "写入数据库时失败"
            else:
                data["result"] = "success"
                d_id = dao.get_id_by_department(department_name)
                u_id = dao.get_id_by_username("root")
                if d_id and u_id:
                    dao.sava_permission(u_id, d_id, "reboot,on,off,")
        else:
            data["result"] = "fail"
            data["errorinfo"] = "提交的信息不完整"
    return jsonify(data)


@application.route("/admin/update_department", methods=["POST"])
@login_required
def update_department():
    username = session.get("user")
    data = {}
    if username != "root":
        data["result"] = "fail"
        data["errorinfo"] = "权限不足"
    else:
        d_name = request.form.get("d_name")
        d_id = request.form.get("d_id")
        if d_name and d_id:
            try:
                int(d_id)
            except:
                data["result"] = "fail"
                data["errorinfo"] = "参数不正确"
                return jsonify(data)
            rowcount = dao.update_department(int(d_id), d_name)
            if rowcount == 0:
                data["result"] = "fail"
                data["errorinfo"] = "数据库中更新失败"
            else:
                data["result"] = "success"
        else:
            data["result"] = "fail"
            data["errorinfo"] = "参数不全"
    return jsonify(data)


@application.route("/admin/get_staff_list", methods=["POST"])
@login_required
def get_staff_list():
    data = {}
    d_id = request.form.get("d_id")
    if d_id:
        username = session.get("user")
        u_id = dao.get_id_by_username(username)
        if u_id:
            permission_list = dao.list_permission_by_user(u_id)
            for permission in permission_list:
                if permission["d_id"] == int(d_id):
                    staff_list = dao.list_staff_by_department(int(d_id))
                    data["staff_list"] = staff_list
    return jsonify(data)


@application.route("/admin/get_permission", methods=["POST"])
@login_required
def get_permission():
    data = {}
    u_id = request.form.get("u_id")
    permission_dict = {}
    if u_id:
        permission_list = dao.list_permission_by_user(u_id)
        for permission in permission_list:
            permission_dict[permission["d_id"]] = permission["permission"].split(",")
        data["permission_dict"] = permission_dict
    return jsonify(data)


@application.route("/admin/staff_manage_page")
@login_required
def staff_manage_page():
    username = session.get("user")
    if username != "root":
        abort(403)
    else:
        department_list = dao.list_department()
        active2 = {"5": "active"}
        return render_template("staff_manage.html", active="admin", title="管理页面",
                               active2=active2, username=username, department_list=department_list)


@application.route("/admin/delete_staff", methods=["POST"])
@login_required
def delete_staff():
    data = {}
    username = session.get("user")
    if username != "root":
        data["result"] = "fail"
        data["errorinfo"] = "权限不足"
        return jsonify(data)
    s_id = request.form.get("s_id")
    if s_id:
        try:
            int(s_id)
        except:
            data["result"] = "fail"
            data["errorinfo"] = "参数不正确"
            return jsonify(data)
        rowcount = dao.remove_staff_by_id(int(s_id))
        if rowcount == 0:
            data["result"] = "fail"
            data["errorinfo"] = "从数据库中删除失败"
        else:
            data["result"] = "success"
            dao.update_vm_set_no_owner(int(s_id))
    else:
        data["result"] = "fail"
        data["errorinfo"] = "参数不全"
    return jsonify(data)


@application.route("/admin/update_staff", methods=["POST"])
@login_required
def update_staff():
    data = {}
    username = session.get("user")
    if username != "root":
        data["result"] = "fail"
        data["errorinfo"] = "权限不足"
        return jsonify(data)
    s_id = request.form.get("s_id")
    s_name = request.form.get("s_name")
    d_id = request.form.get("d_id")
    if s_id and s_name and d_id:
        try:
            int(s_id)
            int(d_id)
        except:
            data["result"] = "fail"
            data["errorinfo"] = "参数不正确"
            return jsonify(data)
        rowcount = dao.update_staff(int(s_id), s_name, int(d_id))
        if rowcount == 0:
            data["result"] = "fail"
            data["errorinfo"] = "数据库中更新失败"
        else:
            data["result"] = "success"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "参数不全"
    return jsonify(data)


@application.route("/admin/add_staff", methods=["POST"])
@login_required
def add_staff():
    data = {}
    username = session.get("user")
    if username != "root":
        data["result"] = "fail"
        data["errorinfo"] = "权限不足"
        return jsonify(data)
    s_name = request.form.get("s_name")
    d_id = request.form.get("d_id")
    if s_name and d_id:
        try:
            int(d_id)
        except:
            data["result"] = "fail"
            data["errorinfo"] = "参数不正确"
            return jsonify(data)
        rowcount = dao.save_staff(s_name, int(d_id))
        if rowcount == 0:
            data["result"] = "fail"
            data["errorinfo"] = "数据库中更新失败"
        else:
            data["result"] = "success"
    else:
        data["result"] = "fail"
        data["errorinfo"] = "参数不全"
    return jsonify(data)
