import struct
import zlib

from .enums import commands
from .utils import validate_mac_addr
from .payload import Acknowledgement, Configuration

MIN_PACKET_LENGTH = 17
MAX_PACKET_LENGTH = 1048


class Message:
    """An IPAssign packet has the following structure:

        [header]      # 14 bytes
        [destination] # 6 bytes, 6 x uint8
        [payload]     # variable length, 0 to 1024 bytes
        [checksum]    # 4 bytes, uint32, little endian

    [destination] is the mac address of the target device. When broadcasting,
                 this address is set to a single byte with value 0x00.
    [payload] is the data sent to the target device.
    [checksum] the crc32 of `[header][destination][payload]`, encoded in little
               endian, then appended to the packet.
    [header] has the following structure:

        [source]        # 6 bytes, 6 x uint8
        [target count]  # 2 byte, uint16
        [packet number] # 2 bytes, uint16
        [command]       # 2 bytes, uint16
        [payload size]  # 2 bytes, uint16

    [source] is the mac address of the device emitting the packet.
    [target count] is set to 0 when broadcasting to the whole group,
                   or 1 when targeting a specific device.
    [packet number] is the packet count sent by this device.
    [command] is one of the predefined commands, eg. set hostname, see
              ipassign.commands for available commands.
    [payload size] describes the quantity of bytes in the payload to read.


    `target count` is called so, to maintain consistency with other legacy
    code. It was originally envisioned that several devices could be targeted
    by a single message, hence its uint16 format.
    In practice, however, it is effectively used as a boolean: it should be
    understood as `is_not_broadcasting`.

    Here is a broadcast message, represented in hex:

        0x78 0x45 0xC4 0xF7 0x8F 0x48   # mac
        0x00                            # target count (broadcast)
        0x00 0x01                       # packet number
        0x00 0x02                       # command (request for parameters)
        0x00 0x00                       # payload length
        0x00                            # destination mac, truncated to 1 byte.
        0x31 0x8F 0x64 0x48             # checksum

    Note, had data been sent, it would have been located between the
    destination mac and the checksum.
    This is therefore the smallest message that can be sent.
    """
    packno = 0

    def __init__(self, source=None, packet_number=None,
                 command=None, destination=None, payload=b''):
        self.source = source

        if packet_number is None:
            packet_number = Message.packno + 1
        self.packet_number = packet_number
        Message.packno = self.packet_number

        if not isinstance(command, commands):
            raise TypeError('expected a command enum')
        if destination is None and command is not commands.REQUEST_CONFIG:
            raise ValueError('Only commands.REQUEST_CONFIG can omit the '
                             'destination. Other commands must include a '
                             'destination mac address')
        self.command = command
        self.destination = destination

        self.payload = payload

    @property
    def source(self):
        return ':'.join([hex(b)[2:].zfill(2) for b in self._source])

    @source.setter
    def source(self, val):
        ok, val = validate_mac_addr(val)
        if not ok:
            raise ValueError(val)
        self._source = val

    @property
    def destination(self):
        if self._dest is not None:
            return ':'.join([hex(b)[2:].zfill(2) for b in self._dest])

    @destination.setter
    def destination(self, val):
        if val is not None:
            ok, val = validate_mac_addr(val)
            if not ok:
                raise ValueError(val)
        self._dest = val

    @property
    def target_count(self):
        return int(self._dest is not None)

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, val):
        if isinstance(val, (Acknowledgement, Configuration)):
            pass
        elif isinstance(val, bytes):
            if len(val) == 0:
                pass
            elif len(val) == 56:
                val = Configuration.from_bytes(val)
            elif len(val) == 4:
                val = Acknowledgement.from_bytes(val)
            else:
                raise ValueError(f'Length must be 0, 4, or 56, not {len(val)}')
        else:
            raise TypeError(f'Payload should be bytes, not {type(val)}')
        self._payload = val

    @property
    def __bytes(self):
        ret = struct.pack('BBBBBB', *self._source)
        ret += struct.pack('H', self.target_count)
        ret += struct.pack('H', self.packet_number)
        ret += struct.pack('H', self.command.value)
        ret += struct.pack('H', len(self.payload))
        if self.target_count:
            ret += struct.pack('BBBBBB', *self._dest)

        if isinstance(self.payload, bytes):
            ret += self.payload
        else:
            ret += self.payload.to_bytes()
        return ret

    @property
    def checksum(self):
        b = self.__bytes
        checksum = zlib.crc32(b)
        return checksum

    def to_bytes(self):
        ret = self.__bytes
        ret += struct.pack('I', self.checksum)
        return ret

    @classmethod
    def from_bytes(cls, barray):
        if not isinstance(barray, bytes):
            raise TypeError(f'Expected bytes, not {type(barray)}')
        if not MIN_PACKET_LENGTH < len(barray) < MAX_PACKET_LENGTH:
            msg = ('A valid array has length between 18 and 1048, '
                   f'not {len(barray)}.')
            raise ValueError(msg, barray, len(barray))

        packet = barray[:-4]

        expected, = struct.unpack('I', barray[-4:])
        calculated = zlib.crc32(packet)
        assert expected == calculated, (f'Invalid CRC! Got {expected} '
                                        f'but calculated {calculated}')

        source = packet[:6]
        source = struct.unpack('BBBBBB', source)
        target_count = packet[6:8]
        target_count, = struct.unpack('H', target_count)
        packet_no = packet[8:10]
        packet_no, = struct.unpack('H', packet_no)
        cmd = packet[10:12]
        cmd, = struct.unpack('H', cmd)
        cmd = commands(cmd)

        payload_len = packet[12:14]
        payload_len, = struct.unpack('H', payload_len)

        dest = None
        if target_count:
            dest = packet[14:20]
            dest = struct.unpack('BBBBBB', dest)

        payload = packet[20:]
        assert len(payload) == payload_len, ('Payload lengths do not match: '
                                             f'was told {payload_len} but '
                                             f'calculated {len(payload)} '
                                             f'{payload}')

        return Message(source, packet_no, cmd, dest, payload)

    def __len__(self):
        return len(self.to_bytes())

    def __eq__(self, other):
        if isinstance(other, Message):
            other = other.to_bytes()
        return self.to_bytes() == other

    def __str__(self):
        dest = 'BROADCAST' if self.destination is None else self.destination
        payload = 'none'
        if isinstance(self.payload, (Acknowledgement, Configuration)):
            payload = '\n            '.join([line for line in
                                             str(self.payload).split('\n')])
        ret = f"""[header]
    [source]       = {self.source}
    [target count] = {self.target_count}
    [packet no]    = {self.packet_number}
    [command]      = {self.command.name} [{hex(self.command.value)}]
    [payload len]  = {len(self.payload)}
[destination] = {dest}
[payload] = {payload}
[checksum] = {hex(self.checksum)}"""
        return ret

    def __repr__(self):
        return f'Message.from_bytes({self.to_bytes()})'
