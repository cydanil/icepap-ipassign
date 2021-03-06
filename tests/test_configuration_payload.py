
import pytest

from ipassign import Configuration
from test_data import CONFIGURATION


def test_instantiation():
    expected = """[configuration]
    [target id]   = 00:0b:ad:c0:ff:ee
    [ip address]  = 8.8.8.8
    [broadcast]   = 172.24.155.25
    [netmask]     = 255.255.255.0
    [gateway]     = 172.24.155.99
    [mac address] = 00:0b:ad:c0:ff:ee
    [flags]       =
    [hostname]    = yolo"""

    p = Configuration(target_id=[0x00, 0x0B, 0xAD, 0xC0, 0xFF, 0xEE],
                      ip=b'\x08\x08\x08\x08',
                      bc=b'\xac\x18\x9b\x19',
                      nm=b'\xff\xff\xff\x00',
                      gw=b'\xac\x18\x9bc',
                      mac=[0x00, 0x0B, 0xAD, 0xC0, 0xFF, 0xEE],
                      hostname="yolo",
                      reboot=False, dynamic=False, flash=False)
    assert str(p) == expected

    pp = Configuration(target_id="00:0B:AD:C0:FF:EE",
                       ip="8.8.8.8",
                       bc="172.24.155.25",
                       nm="255.255.255.0",
                       gw="172.24.155.99",
                       mac="00:0B:AD:C0:FF:EE",
                       hostname="yolo")

    assert str(pp) == expected
    assert p == pp

    repr_ = "Configuration.from_bytes(b'\\x00\\x0b\\xad\\xc0\\xff\\xee\\x08\\x08\\x08\\x08\\xac\\x18\\x9b\\x19\\xff\\xff\\xff\\x00\\xac\\x18\\x9bc\\x00\\x0b\\xad\\xc0\\xff\\xee\\x00\\x00\\x00\\x00yolo\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00')"  # noqa
    assert repr(p) == repr_


def test_deserialisation():
    p = Configuration.from_bytes(CONFIGURATION)
    assert isinstance(p, Configuration)

    expected = """[configuration]
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
    p = Configuration.from_bytes(CONFIGURATION)
    assert p.to_bytes() == CONFIGURATION

    with pytest.raises(ValueError):
        p.hostname = 'attahostnameboytheydontmakethemlikedisnomore'


def test_equality():
    p = Configuration.from_bytes(CONFIGURATION)
    assert p == CONFIGURATION

    pp = Configuration.from_bytes(CONFIGURATION)
    assert pp == p
