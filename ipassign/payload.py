from ipaddress import AddressValueError, IPv4Address
import struct

from .enums import acknowledgements
from .utils import validate_mac_addr


class Configuration:
    """An IcePap IPAssign Configuration payload is either a device's current
    network configuration, or one it should apply.
    The payload has the following structure:

        [icepap id]    # 6 bytes, 6 x uint8
        [ip address]   # 4 bytes, uint32, little endian
        [broadcast]    # ditto
        [netmask]      # ditto
        [gateway]      # ditto
        [mac address]  # 6 bytes, 6 x uint8
        [flags]        # 2 bytes, uint32
        [hostname]     # 24 bytes, ascii string

    [icepap id] is the mac address of the device providing or applying the
                config.
    [ip address] is this configuration's address.
    [broadcast] is this configuration's broadcast address.
    [netmask] is this configuration's netmask.
    [gateway] is this configuration's gateway address.
    [mac address] is this configuration's mac address.
    [flags] are the actions the device should do upon applying a new
            configuration.
    [hostname] is this configuration's hostname.

    The device can be asked to perform one of three actions upon applying a new
    configuration. These are set in the [flags] field and are:
        reboot (first bit set);
        dynamically apply the changes (second bit set);
        write them to flash (third bit set).
    """

    def __init__(self, target_id, ip, bc, nm, gw, mac, hostname,
                 reboot=False, dynamic=False, flash=False):
        self.target_id = target_id
        self.ip = ip
        self.bc = bc
        self.nm = nm
        self.gw = gw
        self.mac = mac
        self.reboot = reboot
        self.dynamic = dynamic
        self.flash = flash
        self.hostname = hostname

    @property
    def target_id(self):
        return ":".join([hex(b)[2:].zfill(2) for b in self._target_id])

    @target_id.setter
    def target_id(self, val):
        ok, val = validate_mac_addr(val)
        if not ok:
            raise ValueError(val)
        self._target_id = val

    @property
    def mac(self):
        return ":".join([hex(b)[2:].zfill(2) for b in self._mac])

    @mac.setter
    def mac(self, val):
        ok, val = validate_mac_addr(val)
        if not ok:
            raise ValueError(val)
        self._mac = val

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, val):
        try:
            val = IPv4Address(val)
        except AddressValueError:
            raise ValueError(val) from None
        self._ip = val

    @property
    def bc(self):
        return self._bc

    @bc.setter
    def bc(self, val):
        try:
            val = IPv4Address(val)
        except AddressValueError:
            raise ValueError(val) from None
        self._bc = val

    @property
    def nm(self):
        return self._nm

    @nm.setter
    def nm(self, val):
        try:
            val = IPv4Address(val)
        except AddressValueError:
            raise ValueError(val) from None
        self._nm = val

    @property
    def gw(self):
        return self._gw

    @gw.setter
    def gw(self, val):
        try:
            val = IPv4Address(val)
        except AddressValueError:
            raise ValueError(val) from None
        self._gw = val

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, val):
        if 24 < len(val):
            raise ValueError('hostname too long, should be max. 24')
        self._hostname = val

    @classmethod
    def from_bytes(cls, barray):
        if not isinstance(barray, bytes):
            raise TypeError(f'Expected bytes, not {type(barray)}')
        if not len(barray) == 56:
            raise ValueError(f'A valid payload has len 56, not {len(barray)}.')

        target_id = barray[:6]
        target_id = struct.unpack('BBBBBB', target_id)
        ip = barray[6:10]
        ip = IPv4Address(ip)
        bc = barray[10:14]
        bc = IPv4Address(bc)
        nm = barray[14:18]
        nm = IPv4Address(nm)
        gw = barray[18:22]
        gw = IPv4Address(gw)
        mac = barray[22:28]
        mac = struct.unpack('BBBBBB', mac)

        flags = barray[28:32]
        flags, = struct.unpack('I', flags)
        reboot = bool((flags >> 0) & 1)
        dynamic = bool((flags >> 1) & 1)
        flash = bool((flags >> 2) & 1)

        hostname = barray[32:].decode().strip('\x00')

        return Configuration(target_id, ip, bc, nm, gw, mac,
                             hostname, reboot, dynamic, flash)

    def to_bytes(self):
        ret = struct.pack('BBBBBB', *self._target_id)
        ret += self._ip.packed
        ret += self._bc.packed
        ret += self._nm.packed
        ret += self._gw.packed
        ret += struct.pack('BBBBBB', *self._mac)

        flags = 0
        if self.reboot:
            flags += 1 << 0
        if self.dynamic:
            flags += 1 << 1
        if self.flash:
            flags += 1 << 2
        ret += struct.pack('I', flags)

        ret += self.hostname.encode()
        pad = 24 - len(self.hostname)
        ret += b'\x00' * pad
        return ret

    def __str__(self):
        flags = ''
        if self.reboot:
            flags += ' reboot'
        if self.dynamic:
            flags += ' dynamic'
        if self.flash:
            flags += ' flash'
        ret = f"""[configuration]
    [target id]   = {self.target_id}
    [ip address]  = {self.ip}
    [broadcast]   = {self.bc}
    [netmask]     = {self.nm}
    [gateway]     = {self.gw}
    [mac address] = {self.mac}
    [flags]       ={flags}
    [hostname]    = {self.hostname}"""
        return ret

    def __repr__(self):
        return f'Configuration.from_bytes({self.to_bytes()})'

    def __eq__(self, other):
        if isinstance(other, Configuration):
            other = other.to_bytes()
        return self.to_bytes() == other

    def __len__(self):
        return len(self.to_bytes())


class Acknowledgement:
    """An acknowledgment payload has the following structure:

        [packet number] # 2 bytes, uint16
        [error code]    # 2 bytes, uint16

    [packet number] is the packet number refering to the acknowledge packet.
                    If a configuration packet was sent with packet number 5, it
                    is then possible to check that the settings match the ones
                    in the packet of that packet.
    [error code] is a status code of having applied the received settings.
    """
    def __init__(self, packno=0, code=0):
        self.packet_number = packno
        if not isinstance(code, acknowledgements):
            code = acknowledgements(code)
        self.code = code

    @classmethod
    def from_bytes(cls, barray):
        packno, code = struct.unpack('HH', barray)
        return Acknowledgement(packno, code)

    def to_bytes(self):
        return struct.pack('HH', self.packet_number, self.code.value)

    def __str__(self):
        return f"""[acknowledgement]
    [to packet] = {self.packet_number}
    [code]      = {self.code.name} [{hex(self.code.value)}]"""

    def __repr__(self):
        return f'Acknowledgement.from_bytes({self.to_bytes()})'

    def __eq__(self, other):
        if isinstance(other, Acknowledgement):
            other = other.to_bytes()
        return self.to_bytes() == other

    def __len__(self):
        return len(self.to_bytes())
