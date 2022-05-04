import socket


class PyWiThrottle:

    def __init__(self,
                 server_ip=None,
                 server_port=None):
        self.server_ip = server_ip
        self.server_port = server_port

    def connect(self):
        try:
            self.cx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cx.connect((self.server_ip, self.server_port))
            self._register_throttle()
        except:
            print("There was an error")

    def disconnect(self):
        self.cx.close()

    def _register_throttle(self):
        self.cx.send(b"NPyWiThrottle")
        reg_data = self.cx.recv(2048)
