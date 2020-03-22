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
