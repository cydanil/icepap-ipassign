import pytest

from ipassign import acknowledgements, Acknowledgement
from test_data import ACK


def test_acknowledgement_instantiation():
    ack = Acknowledgement(0, 0)
    assert ack.packet_number == 0
    assert ack.code == acknowledgements.OK

    pytest.fail('unfinished tests')

    ack = Acknowledgement.from_bytes(ACK)
    assert ack.packet_number == 0
    assert ack.code == acknowledgements.OK
