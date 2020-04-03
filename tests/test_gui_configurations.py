import os
import sys
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ipa_gui.configurations import NetworkWindow  # noqa : import not at top of file


def test_network_window_validate_ip_range():
    ret = NetworkWindow.validate_ip_range('255.255.255.0',
                                          '192.168.1.102',
                                          '192.168.1.1',
                                          '192.168.1.240')
    assert ret

    ret = NetworkWindow.validate_ip_range('255.255.255.0',
                                          '192.168.1.102',
                                          '192.168.0.1',
                                          '192.168.1.240')
    assert not ret

    ret = NetworkWindow.validate_ip_range('255.255.0.0',
                                          '192.168.1.102',
                                          '192.168.0.1',
                                          '192.168.1.240')
    assert ret

    ret = NetworkWindow.validate_ip_range('255.255.255.0',
                                          '192.108.1.102',
                                          '192.168.1.1',
                                          '192.168.1.240')
    assert not ret
