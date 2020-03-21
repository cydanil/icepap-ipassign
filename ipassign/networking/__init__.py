import socket

# UDP Multicast constants
MULTICAST_ADDR = '225.0.0.37'
MULTICAST_PORT = 12345


def is_known_hostname(name: str) -> bool:
    try:
        return socket.gethostbyname(name)
    except socket.gaierror:
        return False


__all__ = [is_known_hostname, MULTICAST_ADDR, MULTICAST_PORT]
