#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
import contextlib
from myapp import application


@contextlib.contextmanager
def open_connection(host, port, user, passwd, db, charset):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # cursor = conn.cursor()
        yield conn, cursor
    except Exception as e:
        print(str(e))
        yield None, None
    finally:
        try:
            conn.close()
            cursor.close()
        except:
            pass

#t_user表
def save_user(username, password_md5_str):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return 0
        try:
            rowcount = cur.execute("INSERT INTO t_user(username, password) VALUES(%s, %s)", [username, password_md5_str])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return 0


def get_password(username):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT password FROM t_user WHERE username = %s", [username])
            result = cur.fetchone()
            if result:
                return result["password"]
            else:
                return None
        except Exception as e:
            print(str(e))
            return None


def get_id_by_username(username):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id FROM t_user WHERE username = %s", [username])
            result = cur.fetchone()
            if result:
                return result["id"]
            else:
                return None
        except Exception as e:
            print(str(e))
            return None


def update_password(username, password_md5_str):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return 0
        try:
            rowcount = cur.execute("UPDATE t_user set password = %s WHERE username = %s", [password_md5_str, username])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return 0


def list_user():
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, username FROM t_user")
            user_list = cur.fetchall()
            return user_list
        except Exception as e:
            print(str(e))
            return None

#t_permission表
def sava_permission(u_id, d_id, permission):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            rowcount = cur.execute("INSERT INTO t_permission(u_id, d_id, permission) VALUES(%s, %s, %s)",
                                   [u_id, d_id, permission])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return None


def remove_permission_by_user(u_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            rowcount = cur.execute("DELETE FROM t_permission WHERE u_id = %s", [u_id])
            conn.commit()
            return rowcount
        except Exception as e:
            conn.rollback()
            print(str(e))
            return None


def list_permission_by_user(u_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, u_id, d_id, permission FROM t_permission WHERE u_id = %s", [u_id])
            permission_list = cur.fetchall()
            return permission_list
        except Exception as e:
            print(str(e))
            return None

#t_department表
def save_department(name):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            rowcount = cur.execute("INSERT INTO t_department(name) VALUES(%s)", [name])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return None


def remove_department(d_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            rowcount = cur.execute("DELETE FROM t_department WHERE id = %s", [d_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return None


def get_id_by_department(name):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id FROM t_department WHERE name = %s", [name])
            d_id = cur.fetchone()
            return d_id
        except Exception as e:
            print(str(e))
            return None


def get_department_by_id(d_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, name FROM t_department WHERE id = %s", [d_id])
            depart = cur.fetchone()
            return depart
        except Exception as e:
            print(str(e))
            return None


def list_department():
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, name FROM t_department")
            depart_list = cur.fetchall()
            return depart_list
        except Exception as e:
            print(str(e))
            return None


def update_department(d_id, name):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return 0
        try:
            rowcount = cur.execute("UPDATE t_department set name = %s WHERE id = %s", [name, d_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return 0

#t_staff表
def remove_staff_by_department(d_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return 0
        try:
            rowcount = cur.execute("DELETE FROM t_staff WHERE d_id = %s", [d_id])
            conn.commit()
            return rowcount
        except Exception as e:
            conn.rollback()
            print(str(e))
            return 0


def list_staff_by_department(d_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, name, d_id FROM t_staff WHERE d_id = %s", [d_id])
            staff_list = cur.fetchall()
            return staff_list
        except Exception as e:
            print(str(e))
            return None


def list_staff():
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, name, d_id FROM t_staff")
            staff_list = cur.fetchall()
            return staff_list
        except Exception as e:
            print(str(e))
            return None


def remove_staff_by_id(s_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return 0
        try:
            rowcount = cur.execute("DELETE FROM t_staff WHERE id = %s", [s_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return 0


def update_staff(s_id, name, d_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return 0
        try:
            rowcount = cur.execute("UPDATE t_staff set name = %s, d_id = %s WHERE id = %s", [name, d_id, s_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return 0


def save_staff(name, d_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return 0
        try:
            rowcount = cur.execute("INSERT INTO t_staff(name, d_id) VALUES (%s, %s)", [name, d_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return 0


def get_staff_by_id(s_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, name, d_id FROM t_staff WHERE id = %s", [s_id])
            staff = cur.fetchone()
            return staff
        except Exception as e:
            print(str(e))
            return None

#t_vm表
def get_vm_by_id(id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, host_ip, name, d_id, s_id FROM t_vm WHERE id = %s", [id])
            vm = cur.fetchone()
            return vm
        except Exception as e:
            print(str(e))
            return None


def list_vm_by_department(d_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, host_ip, name, d_id, s_id FROM t_vm WHERE d_id = %s", [d_id])
            vm_list = cur.fetchall()
            return vm_list
        except Exception as e:
            print(str(e))
            return None


def list_vm_by_staff(s_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            cur.execute("SELECT id, host_ip, name, d_id, s_id FROM t_vm WHERE s_id = %s", [s_id])
            vm_list = cur.fetchall()
            return vm_list
        except Exception as e:
            print(str(e))
            return None


def remove_vm_by_department(d_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            rowcount = cur.execute("DELETE FROM t_vm WHERE d_id = %s", [d_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return None


def remove_vm_by_id(v_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            rowcount = cur.execute("DELETE FROM t_vm WHERE id = %s", [v_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return None


def save_vm(host_ip, name, d_id, s_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            rowcount = cur.execute("INSERT INTO t_vm(host_ip, name, d_id, s_id) VALUES(%s, %s, %s, %s)", [host_ip, name, d_id, s_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return None


def update_vm_set_no_owner(s_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            rowcount = cur.execute("UPDATE t_vm set s_id = -1 WHERE s_id = %s", [s_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return None


def update_vm(v_id, host_ip, name, d_id, s_id):
    with open_connection(host=application.config["HOST"], port=3306,
                         user=application.config["USERNAME"], passwd=application.config["PASSWD"],
                         db=application.config["DBNAME"], charset="utf8") as [conn, cur]:
        if not conn:
            return None
        try:
            rowcount = cur.execute("UPDATE t_vm set host_ip = %s, name = %s, d_id = %s, s_id = %s WHERE id = %s", [host_ip, name, d_id, s_id, v_id])
            conn.commit()
            return rowcount
        except Exception as e:
            print(str(e))
            return None


if __name__ == '__main__':
    with open_connection("localhost", 3306, "root", "Xiejy951", "vm_manage", "utf8") as [conn, cur]:
        if not conn:
            pass
        try:
            cur.execute("SELECT id, host_ip, name, d_id, s_id FROM t_vm WHERE s_id = %s", ["1"])
            vm_list = cur.fetchone()
            print(vm_list)
        except Exception as e:
            print(str(e))

