# -*- coding:utf-8 -*-
import socket
import logging
import time
from logging.handlers import RotatingFileHandler

import myencrypt


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(module)s %(filename)s %(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')

rthandler = RotatingFileHandler("client.log", maxBytes=1024*1024*10, backupCount=3)
rthandler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(module)s %(filename)s %(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')
rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(rthandler)


# Use Python 2.7
class MyClient:
    def __init__(self, host, port, username, password, vm_name):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.vm_name = vm_name

    def poweron(self):
        return self.power_manage("on")

    def poweroff(self):
        return self.power_manage("off")

    def power_manage(self, action):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.host, self.port))
            request = []
            request.append(action)
            request.append(self.vm_name)
            request = "++".join(request)
            time_str = str(int(time.time()))
            self.send_message(client_socket, request, time_str)
            response = self.get_message(client_socket)

            if not response:
                logging.error("connection to {0} broken".format(self.host))
                return False
            if response == "fail":
                logging.error("power{0} {1} failed".format(action, self.vm_name))
                return False
            else:
                logging.info("power{0} {1} success".format(action, self.vm_name))
                return True
        except:
            logging.error("power{0} {1} failed".format(action, self.vm_name))
            return False
        finally:
            if client_socket:
                client_socket.close()

    def get_power_state(self):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.host, self.port))
            request = []
            request.append("get")
            request.append(self.vm_name)
            request = "++".join(request)
            time_str = str(int(time.time()))
            self.send_message(client_socket, request, time_str)
            response = self.get_message(client_socket)
            if not response:
                logging.error("connection to {0} broken".format(self.host))
                return None
            else:
                logging.info("get power state {0}:{1}".format(self.vm_name, response))
                return response
        except:
            logging.error("get power state {0}:failed".format(self.vm_name))
            return None
        finally:
            if client_socket:
                client_socket.close()

    def get_message(self, connection):
        data_bytes = []
        data_length = []
        data_read = 0

        while data_read < 8:
            temp = connection.recv(8 - data_read)
            if temp == "":
                return None
            # temp = temp.decode("utf-8")
            data_length.append(temp)
            data_read = data_read + len(temp)

        data_length = "".join(data_length)
        data_length = int(data_length)

        data_read = 0
        while data_read < data_length:
            temp = connection.recv(min(data_length - data_read, 2048))
            if temp == "":
                return None
            # temp = temp.decode("utf-8")
            data_bytes.append(temp)
            data_read = data_read + len(temp)
        # print result
        data_bytes = "".join(data_bytes)
        temp_list = data_bytes.split("++")
        if len(temp_list) != 2:
            return None
        key = myencrypt.generate_key(bytearray(self.host), bytearray(temp_list[0]))
        response = myencrypt.decrypt(key, temp_list[1])
        if response == None:
            return None
        response = response.decode("utf-8").encode("utf-8")
        return response

    def send_message(self, connection, request, time_str):
        key = myencrypt.generate_key(bytearray(self.host), bytearray(time_str))
        data_bytes = myencrypt.encrypt(key, request)
        # temp_bytes = self.encrypt_message(request, time_str)
        data_bytes = time_str + "++" + data_bytes.decode("utf-8").encode("utf-8")
        data_length = len(data_bytes)
        data_length_bytes = str(data_length)
        if len(data_length_bytes) < 8:
            num = 8 - len(data_length_bytes)
            i = 0
            while i < num:
                i += 1
                data_length_bytes = "0" + data_length_bytes
        # print(temp)
        # print(data_length_str)
        # data_length_str = data_length_str.encode("utf-8")
        connection.sendall(data_length_bytes)
        connection.sendall(data_bytes)


if __name__ == '__main__':
    client = MyClient("192.168.11.249", 54545, "root", "1111111", "client CentOS6.9")
    print(client.get_power_state())
