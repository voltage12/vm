# -*- coding:utf-8 -*-
import socket
import logging
import time
from myapp import myencrypt
from logging.handlers import RotatingFileHandler


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(module)s %(filename)s %(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')
rthandler = RotatingFileHandler("client.log", maxBytes=1024*1024*10, backupCount=3)
rthandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(module)s %(filename)s %(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')
rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(rthandler)


# Use Python 3.5
class MyClient:
    def __init__(self, host, port, vm_name):
        self.host = host
        self.port = port
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
            try:
                if client_socket:
                    client_socket.close()
            except:
                pass

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
            try:
                if client_socket:
                    client_socket.close()
            except:
                pass

    def get_message(self, connection):
        data_bytes = []
        data_length = []
        data_read = 0

        while data_read < 8:
            temp = connection.recv(8-data_read)
            if temp == b"":
                return None
            data_length.append(temp)
            data_read = data_read + len(temp)

        data_length = b"".join(data_length)
        data_length = int(data_length.decode("utf-8"))

        data_read = 0
        while data_read < data_length:
            temp = connection.recv(min(data_length-data_read, 2048))
            if temp == b"":
                return None
            data_bytes.append(temp)
            data_read = data_read + len(temp)
        data_bytes = b"".join(data_bytes)
        temp_list = data_bytes.split(b"++")
        if len(temp_list) != 2:
            return None
        key = myencrypt.generate_key(self.host.encode("utf-8"), temp_list[0])
        response = myencrypt.decrypt(key, temp_list[1])
        if response == None:
            return None
        response = response.decode("utf-8")
        return response

    def send_message(self, connection, request, time_str):
        key = myencrypt.generate_key(self.host.encode("utf-8"), time_str.encode("utf-8"))
        data_bytes = myencrypt.encrypt(key, request.encode("utf-8"))
        data_bytes = time_str.encode("utf-8") + b"++" + data_bytes
        data_length = len(data_bytes)
        data_length_bytes = str(data_length).encode("utf-8")
        if len(data_length_bytes) < 8:
            num = 8 - len(data_length_bytes)
            i = 0
            while i < num:
                i += 1
                data_length_bytes = b"0" + data_length_bytes
        connection.sendall(data_length_bytes)
        connection.sendall(data_bytes)


if __name__ == '__main__':
    client = MyClient("192.168.216.128", 54545, "ubuntu1")
    print(client.get_power_state())
