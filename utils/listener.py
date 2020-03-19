import socket
import struct

from ipassign import MAX_PACKET_LENGTH, Message, MULTICAST_ADDR, MULTICAST_PORT


def main():
    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP,
                    socket.IP_MULTICAST_IF,
                    socket.inet_aton('0.0.0.0'))  # check all interfaces

    mreq = struct.pack('4sL',
                       socket.inet_aton(MULTICAST_ADDR),
                       socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Bind to the server address
    sock.bind(('', MULTICAST_PORT))

    try:
        while True:
            print('\nWaiting for messages...')
            data, address = sock.recvfrom(MAX_PACKET_LENGTH)
            print(Message.from_bytes(data))
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()


if __name__ == '__main__':
    main()
