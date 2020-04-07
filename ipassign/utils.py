import re

# Match lowercase mac address separated by either - or : .
# Credit to https://stackoverflow.com/a/7629690
mac_addr_expr = "[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"


def validate_mac_addr(val):
    if isinstance(val, (list, tuple)):
        if len(val) != 6:
            return False, f'Mac addresses have length 6, not {len(val)}'
        if not all([isinstance(e, int) and e < 256 for e in val]):
            return False, 'Only ints < 256 allowed in list'
        return True, tuple(val)
    if isinstance(val, str) and re.match(mac_addr_expr, val.lower()):
        sep = ':' if ':' in val else '-'
        return True, tuple([int(b, base=16) for b in val.split(sep)])
    return False, f'{val} is not a valid mac address'
