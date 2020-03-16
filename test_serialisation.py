import pytest

from commands import commands
import message
from message import Message

PACKET = b'\x78\x45\xc4\xf7\x8f\x48\x00\x00\x01\x00\x02\x00\x00\x00\x31\x8f\x64\x48'  # noqa


def test_message_object_initialisation(monkeypatch):
    def mock():
        return [0x00, 0x0B, 0xAD, 0xC0, 0xFF, 0xEE]

    setattr(message, 'get_hw_addr', mock)

    Message.packno = 0
    m = Message(command=commands.RESET)
    assert isinstance(m, Message)

    assert m.source == mock()
    assert m.target_id == 0
    assert m.packet_number == 1
    assert m.command == commands.RESET
    assert m.dest is None
    assert m.payload == b''

    m = Message(command=commands.CHANGE_IP)
    assert m.packet_number == 2

    expected = """[header]
    [source]      = 0:b:ad:c0:ff:ee
    [target id]   = 0
    [packet no]   = 2
    [command]     = commands.CHANGE_IP
    [payload len] = 0

[destination] = BROADCAST
[payload] = none
[checksum] = 0xa922c58
"""
    assert str(m) == expected


def test_deserialisation():
    m = Message.from_bytes(PACKET)
    assert isinstance(m, Message)

    with pytest.raises(AssertionError):  # Invalid CRC, due to wrong MAC
        packet = b'xf' + PACKET[2:]
        Message.from_bytes(packet)

    with pytest.raises(TypeError):  # Invalid input
        Message.from_bytes("I'm a string!")

    with pytest.raises(AssertionError):  # Corrupted CRC
        packet = PACKET[:-2] + b'xf'
        Message.from_bytes(packet)

    with pytest.raises(AssertionError):  # Payload length mismatch
        packet = b'xE\xc4\xf7\x8fH\x00\x00\x01\x00\x02\x00\xff\xff\xce\x9dB\xf6'  # noqa
        Message.from_bytes(packet)

    with pytest.raises(ValueError):  # Input too short
        packet = b'xE\xc4\xf7\x8fH\x00\x00\x01\x00\x02\xff\xff\x00'
        Message.from_bytes(packet)

    with pytest.raises(ValueError):  # Input too short
        Message.from_bytes(b'xE\xc4\xf7\x8fH\x00\x00\x01\x00')

    with pytest.raises(ValueError):  # Input too long
        Message.from_bytes(b'x' * 1048)


def test_serialisation():
    m = Message.from_bytes(PACKET)
    assert m.to_bytes() == PACKET
