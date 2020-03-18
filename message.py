"""
An IcePap packet has the following structure:

    [header]      # 14 bytes
    [destination] # 6 bytes, 6 x uint8
    [payload]     # variable length, 0 to 1024 bytes
    [checksum]    # 4 bytes, uint32, little endian

[destination] is the mac address of the target device. When broadcasting,
              this address is set to a single byte with value 0x00.
[payload] is the data sent to the target device.
[checksum] the crc32 of [header][destination][payload], encoded in little
           endian, then appended to the packet.

[header] has the following structure:

    [source]        # 6 bytes, 6 x uint8
    [target id]     # 2 byte, uint16
    [packet number] # 2 bytes, uint16
    [command]       # 2 bytes, uint16
    [payload size]  # 2 bytes, uint16

[source] source is the mac address of the device emitting the packet
[target id] is an IcePaP network id.
[packet number] is the packet count sent by this device.
[command] is one of the predefined commands, eg. set hostname, see
          ipassign.commands
[payload size] describes the quantity of bytes in the payload to read.

Here is a broadcast message, represented in hex:

    0x78 0x45 0xC4 0xF7 0x8F 0x48   # mac
    0x00                            # target id (broadcast)
    0x00 0x01                       # packet number
    0x00 0x02                       # command (request for parameters)
    0x00 0x00                       # payload length
    0x00                            # destination mac, truncated to 1 byte.
    0x31 0x8F 0x64 0x48             # checksum

Note, had data been sent, it would have been located between the destination
mac and the checksum.
This is therefore the smallest message that can be sent.
"""
import struct
import zlib

from commands import commands
from payload import Payload


def get_hw_addr(iface='eth0'):
    with open(f'/sys/class/net/{iface}/address', 'r') as iface:
        mac = iface.readline()
        return [int(b, base=16) for b in mac.split(':')]


class Message:
    packno = 0

    def __init__(self, source=None, target_id=0, packet_number=None,
                 command=None, destination=None, payload=b''):
        self.source = source
        self.target_id = target_id

        if packet_number is None:
            packet_number = Message.packno + 1
        self.packet_number = packet_number
        Message.packno = self.packet_number

        if not isinstance(command, commands):
            raise TypeError('expected a command enum')
        self.command = command

        self.dest = destination
        self.payload = payload

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, val):
        if isinstance(val, str):
            val = [int(b, base=16) for b in val.split(':')]
        if not hasattr(val, '__iter__') or len(val) != 6:
            print('source should be 6 uint8, setting hw mac address')
            val = get_hw_addr()
        self._source = val

    @property
    def dest(self):
        return self._dest

    @dest.setter
    def dest(self, val):
        if isinstance(val, str):
            val = [int(b, base=16) for b in val.split(':')]
        if not hasattr(val, '__iter__') or len(val) != 6:
            val = None
        self._dest = val

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, val):
        if isinstance(val, Payload):
            pass
        elif isinstance(val, bytes):
            if len(val) != 0:
                val = Payload.from_bytes(val)
        else:
            raise TypeError(f'Payload should be bytes, not {type(val)}')
        self._payload = val

    @property
    def __bytes(self):
        ret = struct.pack('BBBBBB', *self.source)
        ret += struct.pack('H', self.target_id)
        ret += struct.pack('H', self.packet_number)
        ret += struct.pack('H', self.command.value)
        ret += struct.pack('H', len(self.payload))
        if self.target_id != 0:
            ret += struct.pack('BBBBBB', *self.dest)

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
        if not 17 < len(barray) < 1048:
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
        target_id = packet[6:8]
        target_id, = struct.unpack('H', target_id)
        packet_no = packet[8:10]
        packet_no, = struct.unpack('H', packet_no)
        cmd = packet[10:12]
        cmd, = struct.unpack('H', cmd)
        cmd = commands(cmd)

        payload_len = packet[12:14]
        payload_len, = struct.unpack('H', payload_len)

        dest = [0x00]
        if target_id != 0:
            dest = packet[14:20]
            dest = struct.unpack('BBBBBB', dest)

        payload = packet[20:]
        assert len(payload) == payload_len, 'Payload lengths do not match'

        return Message(source, target_id, packet_no, cmd, dest, payload)

    def __len__(self):
        return len(self.to_bytes())

    def __eq__(self, other):
        if isinstance(other, Message):
            other = other.to_bytes()
        return self.to_bytes() == other

    def __str__(self):
        source = ':'.join([hex(b)[2:].zfill(2) for b in self.source])
        dest = 'BROADCAST'
        if self.dest is not None:
            dest = ':'.join([hex(b)[2:].zfill(2) for b in self.dest])
        payload = self.payload if self.payload else '[payload] = none'
        ret = f"""[header]
    [source]      = {source}
    [target id]   = {self.target_id}
    [packet no]   = {self.packet_number}
    [command]     = {self.command}
    [payload len] = {len(self.payload)}
[destination] = {dest}
{payload}
[checksum] = {hex(self.checksum)}"""
        return ret

    def __repr__(self):
        return f'Message.from_bytes("{self.to_bytes()}")'
