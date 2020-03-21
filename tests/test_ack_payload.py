import pytest

from ipassign import acknowledgements, Acknowledgement


def test_acknowledgement_instantiation():
    ack = Acknowledgement(0, 0)
    assert isinstance(ack, Acknowledgement)
    assert ack.packet_number == 0
    assert ack.code == acknowledgements.OK

    pytest.fail('unfinished tests')
