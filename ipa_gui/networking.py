import socket
import struct

import netifaces

from PyQt5.QtCore import pyqtSignal, QObject

from ipassign import (commands, Configuration, MAX_PACKET_LENGTH, Message,
                      MULTICAST_ADDR, MULTICAST_PORT)

NETWORK = (MULTICAST_ADDR, MULTICAST_PORT)
IP_ASSIGN_MAC = "00:D1:5E:A5:ED:00"


class NetworkInterface(QObject):
    """This object is the only creator of Message objects.
    The rest of the application deals with Configuration objects.

    This is designed such that the Message number keep increasing in an orderly
    fashion.

    This object connect to all interfaces.
    This object is designed to handle messages serially. Its architecture does
    not lend itself to parallelized operations.

    The motivation for this class to inherit QObject is to send log messages
    via signals to the logging window.
    """

    log = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP,
                        socket.IP_MULTICAST_IF,
                        socket.inet_aton('0.0.0.0'))

        # Tell the operating system to add the socket to the multicast group
        # on all interfaces.
        group = socket.inet_aton(MULTICAST_ADDR)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        mreq = socket.inet_aton(MULTICAST_ADDR) + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Set a timeout on blocking listening
        sock.settimeout(0.2)

        # Bind to the server address
        sock.bind(('', MULTICAST_PORT))
        self.sock = sock

        self.mac = IP_ASSIGN_MAC

    def do_discovery(self) -> dict:
        """Send a requests for configurations, and return a dictionary of
        {mac address (str): Configuration}"""
        message = Message(source=self.mac,
                          command=commands.REQUEST_CONFIG,
                          payload=b'')
        self.log.emit(f'Doing discovery:\n{str(message)}')
        self.sock.sendto(message.to_bytes(), NETWORK)

        ret = dict()
        while True:
            for _ in range(255):  # TODO: Find a better way to loop
                try:
                    data, address = self.sock.recvfrom(MAX_PACKET_LENGTH)
                except socket.timeout:
                    return ret
                message = Message.from_bytes(data)

                if message.source == self.mac:
                    continue  # Skip our own messages

                self.log.emit(f'Received:\n{str(message)}')
                if message.command is commands.SEND_CONFIG:
                    ret[message.source] = message.payload
            return ret

    def send_configuration(self, config: Configuration) -> commands:
        message = Message(source=self.mac,
                          destination=config.mac,
                          command=commands.UPDATE_CONFIG,
                          payload=config)
        pack_no = message.packet_number

        self.log.emit(f'Sending configuration:\n{str(message)}')

        self.sock.sendto(message.to_bytes(), NETWORK)

        while True:
            try:
                data, address = self.sock.recvfrom(MAX_PACKET_LENGTH)
                message = Message.from_bytes(data)

                if message.source == self.mac:
                    continue  # Skip our own messages

                self.log.emit(f'Received:\n {str(message)}')
                if message.command is commands.UPDATE_CONFIG_ACK:
                    # We purposefully do not check the payload type
                    # to crash hard if some messed up packet comes our way
                    if message.payload.packet_number == pack_no:
                        return message.payload.code
            except socket.timeout:
                return None


network = NetworkInterface()


def from_hostname(name: str) -> dict:
    try:
        ip = socket.gethostbyname(name)
    except socket.gaierror:
        return False, 'Not a known hostname'

    gw, iface = netifaces.gateways()['default'][netifaces.AF_INET]

    info = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
    nm = info['netmask']
    bc = info['broadcast']

    return True, {'ip': ip, 'gw': gw, 'nm': nm, 'bc': bc}
