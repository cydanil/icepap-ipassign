import socket
import struct

from ipassign import (acknowledgements, Acknowledgement,
                      commands, Configuration, Message, MULTICAST_ADDR,
                      MULTICAST_PORT)

cosmos = "172.24.155.154"
ip = cosmos

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_MULTICAST_IF,
                socket.inet_aton(ip))

# Tell the operating system to add the socket to
# the multicast group on all interfaces.
group = socket.inet_aton(MULTICAST_ADDR)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
mreq = socket.inet_aton(MULTICAST_ADDR) + socket.inet_aton(ip)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Bind to the server address
sock.bind(('', MULTICAST_PORT))

# Create a mock configuration to send ipassign
mac = '00:0B:AD:C0:FF:EE'
config = Configuration(target_id=mac,
                       ip='172.24.155.105',
                       bc='172.24.155.25',
                       nm='255.255.255.0',
                       gw='172.24.155.99',
                       mac=mac,
                       hostname="hi_mom")

message = Message(source=mac,
                  target_id=1,
                  packet_number=0,
                  command=commands.SEND_CONFIG,
                  payload=config,
                  destination='00:22:19:06:bf:58')

while True:
    print('\nwaiting to receive message')
    data, address = sock.recvfrom(1024)
    m = Message.from_bytes(data)
    print(m)

    if m.command is commands.REQUEST_CONFIG:
        sock.sendto(message.to_bytes(), (MULTICAST_ADDR, MULTICAST_PORT))
        message.packet_number += 1

    if (m.command is commands.UPDATE_CONFIG and
       m.dest == "00:0b:ad:c0:ff:ee"):
        message.payload = m.payload

        if not m.payload.reboot:  # ipassign only sends config. payloads
            ack = Acknowledgement(m.packet_number,
                                  code=acknowledgements.OK)
            ack_msg = Message(source=mac,
                              target_id=1,
                              command=commands.UPDATE_CONFIG_ACK,
                              payload=ack,
                              destination='00:22:19:06:BF:58')
            sock.sendto(ack_msg.to_bytes(),
                        (MULTICAST_ADDR, MULTICAST_PORT))

        message.payload.reboot = False
        message.payload.dynamic = False
        message.payload.flash = False
