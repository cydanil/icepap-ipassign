from ipassign import acknowledgements, Acknowledgement
from test_data import ACK


def test_acknowledgement_payload():
    ack = Acknowledgement(0, 0)
    assert ack.packet_number == 0
    assert ack.code == acknowledgements.OK

    ack = Acknowledgement.from_bytes(ACK)
    assert ack.packet_number == 2
    assert ack.code == acknowledgements.OK

    assert ack.to_bytes() == ACK

    ack = Acknowledgement(5, acknowledgements.ERR_BAD_GW)
    assert ack.to_bytes() == b'\x05\x00\x43\x01'

    expected = """[acknowledgement]
    [to packet] = 5
    [code]      = ERR_BAD_GW [0x143]"""
    assert str(ack) == expected
