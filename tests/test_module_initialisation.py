import os
from pywithrottle.pywithrottle import PyWiThrottle


def test_class_instantiation():
    pwt = PyWiThrottle(server_ip="127.0.0.1", server_port=12090)
    pwt.connect()
    assert pwt.connected == True
