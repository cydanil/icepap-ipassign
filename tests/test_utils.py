from ipassign.utils import validate_mac_addr


def test_validate_mac_addr():
    expected = (0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x00)

    ok, val = validate_mac_addr('DE:AD:BE:EF:00:00')
    assert ok
    assert val == expected

    ok, val = validate_mac_addr('DE-AD-BE-EF-00-00')
    assert ok
    assert val == expected

    ok, val = validate_mac_addr([0, 1, 2, 3])
    assert ok is False
    assert val == 'Mac addresses have length 6, not 4'

    ok, val = validate_mac_addr([222, 173, 190, 239, 0, 0])
    assert ok
    assert val == expected

    ok, val = validate_mac_addr([222, 173, 190, 239, 256, 0])
    assert ok is False
    assert val == 'Only ints < 256 allowed in list'

    ok, val = validate_mac_addr(1)
    assert ok is False
    assert val == '1 is not a valid mac address'
