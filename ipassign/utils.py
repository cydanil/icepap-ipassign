"""
IPAssign command definitions.
"""
from enum import Enum
import re
import socket


class commands(Enum):
    REQUEST_CONFIG = 0x0002
    SEND_CONFIG = 0x0003

    RESET = 0x0004
    RESET_ACK = 0x0005

    CHANGE_IP = 0x0006
    CHANGE_IP_ACK = 0x0007

    SEND_RAW_DATA = 0x0008

    SEND_FIRMWARE_DATA = 0x000A
    WRITE_FIRMWARE = 0x000C

    SEND_ASC_DATA = 0x000E

    UPDATE_CONFIG = 0x000F
    UPDATE_CONFIG_ACK = 0x0010


def validate_ip_addr(val):
    if isinstance(val, bytes):
        try:
            socket.inet_ntoa(val)
            return True, val
        except OSError:
            return False, 'Illegal ip address bytes'

    if isinstance(val, str):
        try:
            value = socket.inet_aton(val)
            return True, value
        except (OSError, ValueError):
            return False, 'Illegal ip address string'

    if isinstance(val, (list, tuple)):
        if not all([isinstance(e, int) and e < 256 for e in val]):
            return False, 'Only ints < 256 allowed in list'
        try:
            value = socket.inet_aton('.'.join([str(e) for e in val]))
            return True, value
        except OSError:
            return False, 'Expected only ints < 256 in list'

    return False, f'Expected str, list(int), or bytes, not {type(val)}'


# Match lowercase mac address separated by either - or : .
# Credit to https://stackoverflow.com/a/7629690
mac_addr_expr = "[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"


def validate_mac_addr(val):
    if isinstance(val, (list, tuple)):
        if len(val) != 6:
            return False, f'Mac addresses have length 6, not {len(val)}'
        if not all([isinstance(e, int) and e < 256 for e in val]):
            return False, 'Only ints < 256 allowed in list'
        return True, val
    if isinstance(val, str) and re.match(mac_addr_expr, val.lower()):
        sep = ':' if ':' in val else '-'
        return True, [int(b, base=16) for b in val.split(sep)]
    return False, f'{val} is not a valid mac address'
