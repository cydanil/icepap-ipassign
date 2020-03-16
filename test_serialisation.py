import pytest

from message import Message

PACKET = b'\x78\x45\xc4\xf7\x8f\x48\x00\x00\x01\x00\x02\x00\x00\x00\x31\x8f\x64\x48'  # noqa


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
