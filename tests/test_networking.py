import os
import socket
import sys

import netifaces

sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ipa_gui.networking import from_hostname  # noqa : import not at top of file


def test_from_hostname():
    def mock_socket(val):
        if val == 'known':
            return '172.24.1.105'
        raise socket.gaierror
    setattr(socket, 'gethostbyname', mock_socket)

    def mock_gateways():
        return {'default': {2: ('172.24.154.1', 'eth0')}}
    setattr(netifaces, 'gateways', mock_gateways)

    def mock_ifaddresses(val):
        return {17: [{'addr': '6c:2b:59:e8:5e:51',
                      'broadcast': 'ff:ff:ff:ff:ff:ff'}],
                2: [{'addr': '172.24.155.154',
                     'netmask': '255.255.254.0',
                     'broadcast': '172.24.155.255'}]}
    setattr(netifaces, 'ifaddresses', mock_ifaddresses)

    ok, val = from_hostname('known')
    assert ok
    assert val == {'ip': '172.24.1.105',
                   'gw': '172.24.154.1',
                   'nm': '255.255.254.0',
                   'bc': '172.24.155.255'}

    ok, val = from_hostname('unknown')
    assert not ok
    assert val == 'Not a known hostname'
