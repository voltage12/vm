import socket
import threading
import string
import subprocess
import logging


logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(module)s  %(filename)s  %(funcName)s [line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='server.log',
                filemode='w')


console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(module)s  %(filename)s  %(funcName)s [line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class MyServer():
    def __init__(self, host='0.0.0.0', port=54545):
        try:
            addr=(host,port)
            self.port = port
            self.server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.server_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
            self.server_socket.bind(addr)
            self.server_socket.listen(5)
            print("create a server socket,listen port:", self.port)
            self.close = False
        except Exception,e :
            print("can't create a server socket,listen port:", self.port)
            # self.close = True
            if self.server_socket:
                self.server_socket.close()
            exit(1)

    def main(self):
        while 1 :
            try :
                print("wait for connecting ...")
                client_socket, addr = self.server_socket.accept()
                addrStr = addr[0]+':'+str(addr[1])
                print('connect from', addrStr)
                ct = ClientThread(client_socket, addrStr)
                ct.start()
            except KeyboardInterrupt:
                self.close=True
                client_socket.close()
                self.server_socket.close()
                print('KeyboardInterrupt:Ctrl+C')
                exit(1)


class ClientThread(threading.Thread):
    def __init__(self, client_socket, addr):
        super(ClientThread,self).__init__()

        self.client_socket = client_socket
        self.addr = addr
        self.timeout = 60
        client_socket.settimeout(self.timeout)
        # self.cf = tcpClient.makefile('rw',0)

    def run(self):
        try:
            connection = self.client_socket
            # self.logger.info("connection from", connection.client_address[0])
            infos = self.get_message(connection)
            if not infos:
                print("connection from {0} broken".format(self.addr))
                return

            print("command from {0}:{1} {2}".format(self.addr, infos[2], infos[3]))
            username = infos[0].strip()
            password = infos[1].strip()
            cmd = infos[2]

            if not self.check_authorization(username, password):
                self.send_message("fail:wrong username or password")
                print(self.addr,"give a wrong username or password")
                return

            if cmd == "on":
                if self.poweron(infos[3]):
                    self.send_message("success")
                    print("poweron {0} success".format(infos[3]))
                else:
                    self.send_message("fail:vm {0} poweron failed".format(infos[3]))
                    print("poweron {0} fail".format(infos[3]))
            elif cmd == "off":
                if self.poweroff(infos[3]):
                    self.send_message("success")
                    print("poweroff {0} success".format(infos[3]))
                else:
                    self.send_message("fail:vm {0} poweroff failed".format(infos[3]))
                    print("poweroff {0} fail".format(infos[3]))
            elif cmd == "get":
                state = self.get_power_state(infos[3])
                if state:
                    self.send_message(state)
                    print("get power state {0} success".format(infos[3]))
                else:
                    self.send_message("None")
                    print("get power state {0} false".format(infos[3]))
        except Exception, e:
            print("some error appear:", str(e))
        finally:
            if connection:
                connection.close()


    def get_message(self, connection):
        cmd = []
        byte_length = []
        byte_read = 0

        while byte_read < 4:
            temp = connection.recv(4-byte_read)
            if temp == "":
                return None
            byte_length.append(temp)
            byte_read = byte_read + len(temp)

        byte_length = string.join(byte_length, "")
        byte_length = int(byte_length)

        byte_read = 0
        while byte_read < byte_length:
            temp = connection.recv(min(byte_length-byte_read, 2048))
            if temp == "":
                return None
            cmd.append(temp)
            byte_read = byte_read + len(temp)
        # print(cmd)
        cmd = string.join(cmd, "")
        return cmd.split("++")


    def send_message(self, message):
        connection = self.client_socket
        data_length = len(message)
        data_length_str = str(data_length)
        if len(data_length_str) < 4:
        	num = 4 - len(data_length_str)
        	i = 0
        	while i < num:
        		i += 1
        		data_length_str = "0" + data_length_str
        connection.sendall(data_length_str)
        connection.sendall(message)


    def check_authorization(self, username, password):
        try:
            f = open("user.txt","r")
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line == "":
                    continue
                user_info = line.split()
                if user_info[0].strip()==username and user_info[1].strip()==password:
                    return True
            return False
        finally:
            if f:
                f.close()


    def update_password(self, username, new_password):
        try:
            os.rename("user.txt", "user.txt.bak")
        except:
            return False
        try:
            f = open("user.txt", "w")
            f.write(username+" "+new_password)
            return True
        except IOError:
            try:
                os.rename("user.txt.bak", "user.txt")
            except:
                return False
        finally:
            try:
                if os.path.exists("user.txt.bak"):
                    os.remove("user.txt.bak")
            except:
                pass
            if f:
                f.close()


    def execute_cmd(self, cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.communicate()


    def poweron(self, vm_name):
        cmd = "vim-cmd vmsvc/getallvm | grep '{0}' | cut -d\" \" -f 1 | xargs -0 -n 1 vim-cmd vmsvc/power.on".format(vm_name)

        std_out, std_err = self.execute_cmd(cmd)

        if std_err == "":
            return True
        else:
            return False


    def poweroff(self, vm_name):
        cmd = "vim-cmd vmsvc/getallvm | grep '{0}' | cut -d\" \" -f 1 | xargs -0 -n 1 vim-cmd vmsvc/power.off".format(vm_name)

        std_out, std_err = self.execute_cmd(cmd)

        if std_err == "":
            return True
        else:
            return False

    def get_power_state(self, vm_name):
        cmd = "vim-cmd vmsvc/getallvm | grep '{0}' | cut -d\" \" -f 1 | xargs -0 -n 1 vim-cmd vmsvc/power.getstate".format(vm_name)

        std_out, std_err = self.execute_cmd(cmd)

        if std_err != "":
            return None
        else:
            return std_out.split()[-1]


if __name__ == "__main__" :
    ser = MyServer()
    ser.main()
