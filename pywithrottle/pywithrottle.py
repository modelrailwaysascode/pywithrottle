"""
SPDX-FileCopyrightText: 2022 Matthew Macdonald-Wallace <matt@doics.co>.

SPDX-License-Identifier: MIT-Modern-Variant
"""
import logging
import socket


class PyWiThrottle(object):
    """
    PyWiThrottle.

    Connect to a WiThrottle server and return a connection object.
    """

    def __init__(self, server_ip=None, server_port=None):
        """
        PyWiThrottle.

        Connect to a WiThrottle server and return a connection object.

        Args:
            server_ip (str): The IP Address of the server
            server_port (int): The TCP Port of the server
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.recv_buffer_size = 2048
        self.logger = logging.getLogger(__name__)
        self.connected = False

    def connect(self):
        """
        connect.

        Connect to the server.
        """
        self.cx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.cx.connect((self.server_ip, self.server_port))
            self.connected = True
        except socket.error:
            self.logger.error('There was an error')

        self._register_throttle()

    def disconnect(self):
        """
        disconnect.

        Disconnect from the server and close the connection.
        """
        self.cx.close()
        self.connected = False

    def _register_throttle(self):
        self.cx.send(b'NPyWiThrottle')
