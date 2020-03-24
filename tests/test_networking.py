import socket

from ipassign import is_known_hostname


def test_is_known_hostname():
    def mock_call(val):
        if val == 'known':
            return '172.24.1.105'
        raise socket.gaierror

    setattr(socket, 'gethostbyname', mock_call)

    assert is_known_hostname('known') == '172.24.1.105'
    assert not is_known_hostname('unknown')
