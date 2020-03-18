# icepap-ipassign

Remotely configure icepap network settings.

IPAssign is a tool developed within ESRF's DEG (Detector and Electronics Group).
Its aim is to provide an easy way to set-up network settings over network, without the need for a complete DaNCE suite.

It does so using UDP broadcast on port `12345`.

## Installing

This package requires Python 3.6+.  
Clone and download this repository, and install it with `pip`:

    pip install .

## Packet Format

An IPAssign packet has the following structure:

    [header]      # 14 bytes
    [destination] # 6 bytes, 6 x uint8
    [payload]     # variable length, 0 to 1024 bytes
    [checksum]    # 4 bytes, uint32, little endian

- `[destination]` is the mac address of the target device. When broadcasting,
                  this address is set to a single byte with value 0x00.
- `[payload]` is the data sent to the target device.
- `[checksum]` the crc32 of `[header][destination][payload]`, encoded in little
               endian, then appended to the packet.
- `[header]` has the following structure:

        [source]        # 6 bytes, 6 x uint8
        [target id]     # 2 byte, uint16
        [packet number] # 2 bytes, uint16
        [command]       # 2 bytes, uint16
        [payload size]  # 2 bytes, uint16

  - `[source]` is the mac address of the device emitting the packet.
  - `[target id]` is an IcePaP network id.
  - `[packet number]` is the packet count sent by this device.
  - `[command]` is one of the predefined commands, eg. set hostname, see
                `ipassign.commands`
  - `[payload size]` describes the quantity of bytes in the payload to read.

Here is the anatomy of a broadcast message:

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

An other example, of a reply to this broadcast hello, is:

```python
from ipassign import Message
pp = b'\x00\x0c\xc6\x69\x13\x2d\x01\x00\x00\x00\x03\x00\x38\x00\x00\x22\x19\x06\xbf\x58\x00\x0c\xc6\x69\x13\x2d\xac\x18\x9b\xde\xac\x18\x9b\xff\xff\xff\xff\x00\xac\x18\x9b\x63\x00\x0c\xc6\x69\x13\x2d\x00\x00\x00\x00\x69\x63\x65\x65\x75\x34\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb3\x57\x23\x0d'

m = Message.from_bytes(pp)

print(m)
[header]
    [source]      = 00:0c:c6:69:13:2d
    [target id]   = 1
    [packet no]   = 0
    [command]     = commands.SEND_PARAMS
    [payload len] = 56
[destination] = 00:22:19:06:bf:58
[payload]
    [target id]   = 00:0c:c6:69:13:2d
    [ip address]  = 172.24.155.222
    [broadcast]   = 172.24.155.255
    [netmask]     = 255.255.255.0
    [gateway]     = 172.24.155.99
    [mac address] = 00:0c:c6:69:13:2d

    [flags]       =
    [hostname]    = iceeu4
[checksum] = 0xd2357b3
```

## Configuration Payload

A payload is either a device's current network configuration, or one it should apply.
The payload has the following structure:

    [icepap id]    # 6 bytes, 6 x uint8
    [ip address]   # 4 bytes, uint32, little endian
    [broadcast]    # ditto
    [netmask]      # ditto
    [gateway]      # ditto
    [mac address]  # 6 bytes, 6 x uint8
    [flags]        # 2 bytes, uint32
    [hostname]     # variable length, 24 bytes max, ascii string

- `[icepap id]` is the mac address of the device providing or applying the config.
- `[ip address]` is this configuration's address.
- `[broadcast]` is this configuration's broadcast address.
- `[netmask]` is this configuration's netmask.
- `[gateway]` is this configuration's gateway address.
- `[mac address]` is this configuration's mac address.
- `[flags]` are the actions the device should do upon applying a new configuration.
- `[hostname]` is this configuration's hostname.

The device can be asked to perform one of three actions upon applying a new
configuration.
These are set in the `[flags]` field and are:

- reboot (first bit set);
- dynamically apply the changes (second bit set);
- write them to flash (third bit set).

Here is configuration payload:

    0x00 0x0C 0xC6 0x69 0x13 0x2D                 # icepap id, a mac address
    0xAC 0x18 0x9B 0xDE 0xAC                      # IP address, 172.24.155.222
    0xAC 0x18 0x9B 0xDE 0xFF                      # broadcast, 172.24.155.255
    0xFF 0xFF 0xFF 0xFF 0x00                      # netmask, 255.255.255.0
    0xAC 0x18 0x9B 0xDE 0x63                      # gateway, 172.24.155.99
    0x00 0x0C 0xC6 0x69 0x13 0x2D                 # reprogrammable mac address
    0x00 0x00                                     # flags, none
    0X74 0X68 0X78 0X63 0X6F 0X72 0X6F 0X6E 0X61  # hostname

## Acknowledgment Payload

An acknowledgment payload has the following structure:

    [packet number] # 2 bytes, uint16
    [error code]    # 2 bytes, uint16

- `[packet number]` is the packet number refering to the acknowledge packet.
                    If a configuration packet was sent with packet number 5,
                    it is then possible to check that the settings match the ones
                    in the packet of that packet.
- `[error code]` is a status code of having applied the received settings.

TODO: Add example payload here.

## Testing

Testing is done with `pytest`:

    pip install .
    pytest -vv
