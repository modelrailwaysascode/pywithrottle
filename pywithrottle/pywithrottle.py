"""
SPDX-FileCopyrightText: 2022 Matthew Macdonald-Wallace <matt@doics.co>.

SPDX-License-Identifier: MIT-Modern-Variant
"""
import logging
import pprint
import re
import socket

from time import sleep


class PyWiThrottle(object):
    """
    PyWiThrottle.

    Connect to a WiThrottle server and return a connection object.
    """

    def __init__(self,
                 server_ip=None,
                 server_port=None,
                 dcc_address_scheme="S"):
        """
        PyWiThrottle.

        Connect to a WiThrottle server and return a connection object.

        Args:
            server_ip (str): The IP Address of the server
            server_port (int): The TCP Port of the server
            dcc_address_scheme (str): A single, upper-case character denoting
                                      short (S) or long (L) DCC Addresses
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.recv_buffer_size = 2048
        self.logger = logging.getLogger(__name__)
        self.pp = pprint.PrettyPrinter(indent=2)
        if dcc_address_scheme not in ["S", "L"]:
            raise Exception
        else:
            self.dcc_address_scheme = dcc_address_scheme
        self._register_throttle()

    def connect(self):
        """
        connect.

        Connect to the server.
        """
        self.cx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.cx.connect((self.server_ip, self.server_port))
        except socket.error:
            self.logger.error('There was an error')

        sleep(0.5)
        # data = self.cx.recv(2048).splitlines()
        # for line in data:
        #    if line:
        #        ln = line.decode()
        #        print(ln )
        #        if re.match("RL(.*)",ln):
        #            self.roster(ln)
        #        if re.match("PPA(.*)",ln):
        #            print("Power" )
        #        if re.match("PTT(.*)",ln):
        #            self.turnoutstate(ln)
        #        if re.match("PTL(.*)",ln):
        #            self.turnout(ln)
        #        if re.match("PRL(.*)",ln):
        #            self.turnout(ln)
        #        if re.match("PTA(.*)",ln):
        #            self.setturnout(ln)
        self.connected = True

    def disconnect(self):
        """
        disconnect.

        Disconnect from the server and close the connection.
        """
        self.cx.send(b'Q\n')
        self.cx.close()
        self.connected = False

    def _register_throttle(self):
        self.connect()
        self.cx.send(b'NPyWiThrottle\n')

    def register_loco(self, dcc_id, roster_id):
        reg_data = f"M0+{self.dcc_address_scheme}{dcc_id}<;>{self.dcc_address_scheme}{dcc_id}\n" # noqa E501
        print(f"Registering loco with command {reg_data}")
        self.cx.send(reg_data.encode('ascii'))
        print(self.cx.recv(2048))

    def function_control(self, loco_id, state, function_id):
        function_string = f"M0A{self.dcc_address_scheme}{loco_id}<;>F{state}{function_id:02d}\n" # noqa E501
        print(f"Sending {function_string} to server")
        self.cx.send(function_string.encode('ascii'))
        print(self.cx.recv(2048))

    def roster(self, data_in):
        print("Roster list")
        self.rosterlist = []
        parse = re.search(
                'RL([0-9]+)\\]\\\\\[(.*)', # noqa W605
                data_in)
        if int(parse.group(1)) > 0:
            for entry in parse.group(2).split(']\['): # noqa W605
                self.rosterlist.append(entry.split('}|{'))
        print('\n'.join(map(str, self.rosterlist)))

    def turnoutstate(self, data_in):
        print("Turnout status")
        self.turnoutstates = {}
        for entry in data_in[6:].split(']\['): # noqa W605
            entrylist = entry.split('}|{')
            if entrylist[1] != 'Turnout':
                self.turnoutstates[entrylist[1]] = entrylist[0]
        self.pp.pprint(self.turnoutstates)

    def turnout(self, data_in):
        print("Turnout list")
        self.turnouts = {}
        for entry in data_in[6:].split(']\['): # noqa W605
            entrylist = entry.split('}|{')
            if entrylist[1]:
                self.turnouts[entrylist[1]] = {
                        'sysname': entrylist[0],
                        'state': entrylist[2]
                        }
            else:
                self.turnouts[entrylist[0]] = {
                        'sysname': entrylist[0],
                        'state': entrylist[2]}
        self.pp.pprint(self.turnouts)

    def setturnout(self, data_in):
        parse = re.search(
                'PTA([0-9])(.*)',
                data_in
                )
        if parse:
            pg1 = parse.group(1)
            print("Turnout: "+parse.group(2)+" "+self.turnoutstates[pg1])

    def route(self, data_in):
        print("Route list")
        routelist = []
        routes = {}
        for entry in data_in[6:].split(']\['): # noqa W605
            entrylist = entry.split('}|{')
            routelist.append(entrylist)
            if entrylist[1]:
                routes[entrylist[1]] = entrylist[0]
            else:
                routes[entrylist[0]] = entrylist[0]

        print('\n'.join(map(str, routelist)))
        self.pp.pprint(routes)
