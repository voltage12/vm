#!/usr/bin/python
# -*- coding: UTF-8 -*-

import hashlib
import threading


class GetPowerStateThread(threading.Thread):
    lock = threading.Lock()

    def __init__(self, client, power_state_dict, cache, vm):
        super(GetPowerStateThread, self).__init__()
        self.client = client
        self.power_state_dict = power_state_dict
        self.cache = cache
        self.vm = vm

    def run(self):
        power_state = self.client.get_power_state()
        try:
            GetPowerStateThread.lock.acquire()
            if power_state:
                self.cache.set(self.vm["id"], power_state, 3600)
                self.power_state_dict[self.vm["id"]] = power_state
            else:
                self.power_state_dict[self.vm["id"]] = "获取失败"
        finally:
            GetPowerStateThread.lock.release()


def get_md5(password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    return md5.hexdigest()


def check_password(password, md5_str):
    if get_md5(password) == md5_str:
        return True
    else:
        return False


if __name__ == '__main__':
    password = input("请输入密码:")
    print(get_md5(password))
