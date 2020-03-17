"""
An IcePap IPAssign payload is either a device's current network configuration,
or one it should apply.
The payload has the following structure:

    [icepap id]    # 6 bytes, 6 x uint8
    [ip address]   # 4 bytes, uint32, little endian
    [broadcast]    # ditto
    [netmask]      # ditto
    [gateway]      # ditto
    [mac address]  # 6 bytes, 6 x uint8
    [flags]        # 2 bytes, uint32
    [hostname]     # 24 bytes, ascii string

[icepap id] is the mac address of the device providing or applying the config.
[ip address] is this configuration's address.
[broadcast] is this configuration's broadcast address.
[netmask] is this configuration's netmask.
[gateway] is this configuration's gateway address.
[mac address] is this configuration's mac address.
[flags] are the actions the device should do upon applying a new configuration.
[hostname] is this configuration's hostname.

The device can be asked to perform one of three actions upon applying a new
configuration. These are set in the [flags] field and are:
    reboot (first bit set);
    dynamically apply the changes (second bit set);
    write them to flash (third bit set).


An IcePap acknowledgment payload has the following structure:

    [packno]     # 2 bytes, uint16
    [error code] # 2 bytes, uint16

[packno] is the packet number refering to the acknowledge packet.
         If a configuration packet was sent with packet number 5, then this
         field will be 5, and you'll know that the configuration sent then was
         treated.
[error code] is a status code of having applied the received settings.
"""
import struct


class Payload:

    def __init__(self, target_id, ip, bc, nm, gw, mac, reboot,
                 dynamic, flash, hostname):
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

    def to_bytes(self):
        assert len(self.hostname) <= 24, 'Provided hostname too long'
        return b''

    @classmethod
    def from_bytes(cls, barray):
        if not isinstance(barray, bytes):
            raise TypeError(f'Expected bytes, not {type(barray)}')
        if not len(barray) == 56:
            raise ValueError(f'A valid payload has len 56, not {len(barray)}.')

        target_id = barray[:6]
        target_id = struct.unpack('BBBBBB', target_id)
        ip = barray[6:10]
        ip = struct.unpack('BBBB', ip)
        bc = barray[10:14]
        bc = struct.unpack('BBBB', bc)
        nm = barray[14:18]
        nm = struct.unpack('BBBB', nm)
        gw = barray[18:22]
        gw = struct.unpack('BBBB', gw)
        mac = barray[22:28]
        mac = struct.unpack('BBBBBB', mac)

        flags = barray[28:32]
        flags, = struct.unpack('I', flags)
        reboot = bool((flags >> 0) & 1)
        dynamic = bool((flags >> 1) & 1)
        flash = bool((flags >> 2) & 1)

        hostname = barray[32:].decode()

        return Payload(target_id, ip, bc, nm, gw, mac,
                       reboot, dynamic, flash, hostname)
