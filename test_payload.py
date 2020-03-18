import pytest
from payload import Payload
from test_data import PAYLOAD


def test_deserialisation():
    p = Payload.from_bytes(PAYLOAD)
    assert isinstance(p, Payload)

    expected = """[payload]
    [target id]   = 00:0c:c6:69:13:2d
    [ip address]  = 172.24.155.222
    [broadcast]   = 172.24.155.255
    [netmask]     = 255.255.255.0
    [gateway]     = 172.24.155.99
    [mac address] = 00:0c:c6:69:13:2d

    [flags]       =
    [hostname]    = iceeu4"""

    assert str(p) == expected


def test_serialisation():
    p = Payload.from_bytes(PAYLOAD)
    assert p.to_bytes() == PAYLOAD

    with pytest.raises(ValueError):
        p.hostname = 'attahostnameboytheydontmakethemlikedisnomore'


def test_equality():
    p = Payload.from_bytes(PAYLOAD)
    assert p == PAYLOAD

    pp = Payload.from_bytes(PAYLOAD)
    assert pp == p
