import socket
import threading
import string
import subprocess
import logging
import time
import myencrypt
from logging.handlers import RotatingFileHandler


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(module)s %(filename)s %(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')

rthandler = RotatingFileHandler("server.log", maxBytes=1024 * 1024 * 10, backupCount=3)
rthandler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(module)s %(filename)s %(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')
rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(rthandler)


# Use Python 2.7
class MyServer():
    def __init__(self, host='0.0.0.0', port=54545):
        try:
            addr = (host, port)
            self.port = port
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.server_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
            self.server_socket.bind(addr)
            self.server_socket.listen(5)
            logging.info("create a server socket,listen port:{0}".format(self.port))
            # self.close = False
        except Exception, e:
            logging.error("can't create a server socket,listen port:{0}".format(self.port))
            logging.error(str(e))
            # self.close = True
            if self.server_socket:
                self.server_socket.close()
            exit(1)

    def main(self):
        logging.info("wait for connecting ...")
        while 1:
            try:
                client_socket, addr = self.server_socket.accept()
                addr_str = addr[0] + ':' + str(addr[1])
                logging.info("connect from {0}".format(addr_str))
                ct = ClientThread(client_socket, addr_str)
                ct.start()
            except KeyboardInterrupt:
                # self.close = True
                if client_socket:
                    client_socket.close()
                self.server_socket.close()
                logging.info('KeyboardInterrupt:Ctrl+C')
                exit(1)


class ClientThread(threading.Thread):
    def __init__(self, client_socket, addr):
        super(ClientThread, self).__init__()

        self.client_socket = client_socket
        self.addr = addr
        self.timeout = 120
        client_socket.settimeout(self.timeout)
        # self.cf = tcpClient.makefile('rw',0)

    def run(self):
        try:
            connection = self.client_socket
            # self.logger.info("connection from", connection.client_address[0])
            request = self.get_message(connection)
            if not request:
                logging.error("connection from {0} broken".format(self.addr))
                return
            request = request.split("++")
            logging.info("command from {0}:{1} {2}".format(self.addr, request[0], request[1]))
            cmd = request[0]
            time_str = str(int(time.time()))
            if cmd == "on":
                if self.poweron(request[1]):
                    self.send_message("success", time_str)
                    logging.info("poweron {0} success".format(request[1]))
                else:
                    self.send_message("fail", time_str)
                    logging.error("poweron {0} fail".format(request[1]))
            elif cmd == "off":
                if self.poweroff(request[1]):
                    self.send_message("success", time_str)
                    logging.info("poweroff {0} success".format(request[1]))
                else:
                    self.send_message("fail".format(request[1]), time_str)
                    logging.error("poweroff {0} fail".format(request[1]))
            elif cmd == "get":
                state = self.get_power_state(request[1])
                if state:
                    self.send_message(state, time_str)
                    logging.info("get power state {0} success".format(request[1]))
                else:
                    self.send_message("None", time_str)
                    logging.error("get power state {0} false".format(request[1]))
            else:
                self.send_message("unknow", time_str)
        except Exception, e:
            logging.error("some error appear:{0}".format(str(e)))
        finally:
            if connection:
                connection.close()

    def get_message(self, connection):
        data_bytes = []
        data_length = []
        data_read = 0

        while data_read < 8:
            temp = connection.recv(8 - data_read)
            if temp == "":
                return None
            data_length.append(temp)
            data_read = data_read + len(temp)

        data_length = string.join(data_length, "")
        data_length = int(data_length)

        data_read = 0
        while data_read < data_length:
            temp = connection.recv(min(data_length - data_read, 2048))
            if temp == "":
                return None
            data_bytes.append(temp)
            data_read = data_read + len(temp)
        # print(cmd)
        data_bytes = string.join(data_bytes, "")
        temp_list = data_bytes.split("++")
        if len(temp_list) != 2:
            return None
        key = myencrypt.generate_key(bytearray(self.get_host_ip()), bytearray(temp_list[0]))
        request = myencrypt.decrypt(key, temp_list[1])
        if request == None:
            return None
        request = request.decode("utf-8").encode("utf-8")
        return request

    def send_message(self, response, time_str):
        connection = self.client_socket
        key = myencrypt.generate_key(bytearray(self.get_host_ip()), bytearray(time_str))
        data_bytes = myencrypt.encrypt(key, response).decode("utf-8").encode("utf-8")
        data_bytes = time_str + "++" + data_bytes
        data_length = len(data_bytes)
        data_length_str = str(data_length)
        if len(data_length_str) < 8:
            num = 8 - len(data_length_str)
            i = 0
            while i < num:
                i += 1
                data_length_str = "0" + data_length_str
        connection.sendall(data_length_str)
        connection.sendall(data_bytes)

    def execute_cmd(self, cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.communicate()

    def poweron(self, vm_name):
        cmd = "vim-cmd vmsvc/getallvm | grep '{0}' | cut -d\" \" -f 1 | xargs -0 -n 1 vim-cmd vmsvc/power.on".format(
            vm_name)
        std_out, std_err = self.execute_cmd(cmd)

        if std_err == "":
            return True
        else:
            return False

    def poweroff(self, vm_name):
        cmd = "vim-cmd vmsvc/getallvm | grep '{0}' | cut -d\" \" -f 1 | xargs -0 -n 1 vim-cmd vmsvc/power.off".format(
            vm_name)
        std_out, std_err = self.execute_cmd(cmd)

        if std_err == "":
            return True
        else:
            return False

    def get_power_state(self, vm_name):
        cmd = "vim-cmd vmsvc/getallvm | grep '{0}' | cut -d\" \" -f 1 | xargs -0 -n 1 vim-cmd vmsvc/power.getstate".format(
            vm_name)
        std_out, std_err = self.execute_cmd(cmd)

        if std_err != "":
            return None
        else:
            return std_out.split()[-1]

    def get_host_ip(self):
        cmd = "vim-cmd hostsvc/net/vnic_info | grep ipAddress"
        std_out, std_err = self.execute_cmd(cmd)

        if std_err != "":
            return None
        else:
            return std_out.split()[2][1:-2].strip()


if __name__ == "__main__":
    ser = MyServer()
    ser.main()
