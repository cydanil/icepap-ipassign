import os
import socket
import sys
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ipa_gui.networking import gethostbyname  # noqa : import not at top of file


def test_gethostbyname():
    def mock_call(val):
        if val == 'known':
            return '172.24.1.105'
        raise socket.gaierror

    setattr(socket, 'gethostbyname', mock_call)

    assert gethostbyname('known') == '172.24.1.105'
    assert not gethostbyname('unknown')
