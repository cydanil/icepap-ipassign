import random
import socket
import string
import struct
import sys

from ipassign import (acknowledgements, Acknowledgement,
                      commands, Configuration, MAX_PACKET_LENGTH,
                      Message, MULTICAST_ADDR, MULTICAST_PORT)

from ipassign.utils import validate_mac_addr

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_MULTICAST_IF,
                socket.inet_aton('0.0.0.0'))

# Tell the operating system to add the socket to
# the multicast group on all interfaces.
group = socket.inet_aton(MULTICAST_ADDR)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
mreq = socket.inet_aton(MULTICAST_ADDR) + socket.inet_aton('0.0.0.0')
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Bind to the server address
sock.bind(('', MULTICAST_PORT))

# Get settings for this session
nack = False
mac = None
if len(sys.argv) > 1:
    if '--nack' in sys.argv:
        nack = True
    for item in sys.argv:
        ok, val = validate_mac_addr(item)
        if ok:
            mac = val

if mac is None:
    mac = ':'.join([hex(random.randint(1, 255))[2:].zfill(2) for
                    _ in range(6)])

hostname = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))

print(f'Working with {mac} and {hostname}, no ack: {nack}')

# Create a mock configuration to send ipassign
config = Configuration(target_id=mac,  # will be overwritten in due time
                       ip='172.24.155.105',
                       bc='172.24.155.25',
                       nm='255.255.255.0',
                       gw='172.24.155.99',
                       mac=mac,
                       hostname=hostname)

message = Message(source=mac,
                  packet_number=0,
                  destination=mac,  # will be overwritten in due time
                  command=commands.SEND_CONFIG,
                  payload=config)

try:
    while True:
        print('\nwaiting to receive message')
        data, address = sock.recvfrom(MAX_PACKET_LENGTH)
        m = Message.from_bytes(data)
        if m.source == mac:
            print('--- Our reply:')
            print('            ', end='')
            print('\n            '.join([line for line in str(m).split('\n')]))
            print('--------------')
        else:
            print(m)

        if m.command is commands.REQUEST_CONFIG:
            message.destination = m.source
            sock.sendto(message.to_bytes(), (MULTICAST_ADDR, MULTICAST_PORT))
            message.packet_number += 1

        if m.command is commands.UPDATE_CONFIG and m.destination == mac:
            message.payload = m.payload

            if not m.payload.reboot and nack is False:
                ack = Acknowledgement(m.packet_number,
                                      code=acknowledgements.OK)
                ack_msg = Message(source=mac,
                                  command=commands.UPDATE_CONFIG_ACK,
                                  payload=ack,
                                  destination=m.source)
                sock.sendto(ack_msg.to_bytes(),
                            (MULTICAST_ADDR, MULTICAST_PORT))

            message.payload.reboot = False
            message.payload.dynamic = False
            message.payload.flash = False
except KeyboardInterrupt:
    pass
