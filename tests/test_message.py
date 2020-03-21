import pytest

from ipassign import Acknowledgement, commands, Message, Configuration
from test_data import ACK, ACK_MSG, PACKET, PAYLOAD, REPLY


def test_message_object_instantiation():
    mac = [0x00, 0x0B, 0xAD, 0xC0, 0xFF, 0xEE]
    Message.packno = 0
    m = Message(source=mac, command=commands.RESET)
    assert isinstance(m, Message)

    assert m.source == '00:0b:ad:c0:ff:ee'
    assert m.target_id == 0
    assert m.packet_number == 1
    assert m.command == commands.RESET
    assert m.dest is None
    assert m.payload == b''

    m = Message(source=mac, command=commands.CHANGE_IP)
    assert m.packet_number == 2

    expected = """[header]
    [source]      = 00:0b:ad:c0:ff:ee
    [target id]   = 0
    [packet no]   = 2
    [command]     = CHANGE_IP [0x6]
    [payload len] = 0
[destination] = BROADCAST
[payload] = none
[checksum] = 0xa922c58"""
    assert str(m) == expected

    m.source = "00:de:ad:be:ef:00"


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


def test_parse_reply():
    m = Message.from_bytes(REPLY)
    assert m.to_bytes() == REPLY
    assert m == REPLY

    expected = """[header]
    [source]      = 00:0c:c6:69:13:2d
    [target id]   = 1
    [packet no]   = 0
    [command]     = SEND_CONFIG [0x3]
    [payload len] = 56
[destination] = 00:22:19:06:bf:58
[configuration]
    [target id]   = 00:0c:c6:69:13:2d
    [ip address]  = 172.24.155.222
    [broadcast]   = 172.24.155.255
    [netmask]     = 255.255.255.0
    [gateway]     = 172.24.155.99
    [mac address] = 00:0c:c6:69:13:2d

    [flags]       =
    [hostname]    = iceeu4
[checksum] = 0xd2357b3"""

    assert str(m) == expected


def test_message_config_payload():
    p = Configuration.from_bytes(PAYLOAD)
    p.reboot = True
    source = "00:0c:c6:69:13:2d"
    target_id = 5
    destination = "00:de:ad:be:ef:00"
    command = commands.UPDATE_CONFIG

    m = Message(source=source,
                target_id=target_id,
                command=command,
                destination=destination,
                payload=p)

    mm = Message(source=source,
                 target_id=target_id,
                 packet_number=1,
                 command=command,
                 destination=destination,
                 payload=PAYLOAD)
    mm.payload.reboot = True

    mmm = Message(source=source,
                  target_id=target_id,
                  packet_number=1,
                  command=command,
                  destination=destination,
                  payload=b'')
    mmm.payload = PAYLOAD
    mmm.payload.reboot = True

    mmmm = Message(source=source,
                   target_id=target_id,
                   packet_number=1,
                   command=command,
                   destination=destination,
                   payload=b'')
    mmmm.payload = p

    print(m)
    print()
    print(mm)
    assert m == mm
    assert mm == mmm
    assert mmm == mmmm


def test_message_ack_payload():
    m = Message.from_bytes(ACK_MSG)
    print(m)
    assert isinstance(m, Message)

    expected = """[header]
    [source]      = 00:0c:c6:69:13:2d
    [target id]   = 1
    [packet no]   = 1
    [command]     = UPDATE_CONFIG_ACK [0x10]
    [payload len] = 4
[destination] = 00:22:19:06:bf:58
[acknowledgement]
    [to packet] = 2
    [code]      = OK [0]
[checksum] = 0x12ec8a45"""

    assert str(m) == expected
    assert m.to_bytes() == ACK_MSG

    p = Acknowledgement.from_bytes(ACK)
    source = "00:0c:c6:69:13:2d"
    target_id = 1
    destination = "00:22:19:06:bf:58"
    command = commands.UPDATE_CONFIG_ACK

    mm = Message(source=source,
                 target_id=target_id,
                 command=command,
                 destination=destination,
                 payload=p)

    assert m == mm
