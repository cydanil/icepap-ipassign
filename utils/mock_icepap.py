import time
import socket
import struct

from ipassign import commands, Message, Payload

cosmos = "172.24.155.154"

ip = cosmos

multicast_group = '225.0.0.37'
server_address = ('', 12345)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_MULTICAST_IF,
                socket.inet_aton(ip))

# Tell the operating system to add the socket to
# the multicast group on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
mreq = socket.inet_aton(multicast_group) + socket.inet_aton(ip)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Bind to the server address
sock.bind(server_address)

# Create a mock configuration to send ipassign
p = Payload(target_id=[0x00, 0x0B, 0xAD, 0xC0, 0xFF, 0xEE],
            ip=[8, 8, 8, 8],
            bc=[172, 24, 155, 25],
            nm=[255, 255, 255, 0],
            gw=[172, 24, 155, 99],
            mac=[0x00, 0x0B, 0xAD, 0xC0, 0xFF, 0xEE],
            hostname="hi_mom",
            reboot=False, dynamic=False, flash=False)
config_message = Message(source="00:0B:AD:C0:FF:EE",
                         target_id=1,
                         packet_number=0,
                         command=commands.SEND_CONFIG,
                         payload=p,
                         destination="00:22:19:06:bf:58")
while True:
    print('\nwaiting to receive message')
    data, address = sock.recvfrom(1024)
    m = Message.from_bytes(data)
    print(m)

    if m.command is commands.REQUEST_CONFIG:
        time.sleep(1)  # Sleep to check for side-effects
        sock.sendto(config_message.to_bytes(), (multicast_group, 12345))
