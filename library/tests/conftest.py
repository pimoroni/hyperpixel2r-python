import sys
import mock
import pytest


@pytest.fixture(scope='function', autouse=False)
def smbus2():
    """Mock smbus module."""
    smbus = mock.MagicMock()
    sys.modules['smbus2'] = smbus
    yield smbus
    del sys.modules['smbus2']


@pytest.fixture(scope='function', autouse=False)
def GPIO():
    """Mock RPi.GPIO module."""

    GPIO = mock.MagicMock()
    # Fudge for Python < 37 (possibly earlier)
    sys.modules['RPi'] = mock.Mock()
    sys.modules['RPi'].GPIO = GPIO
    sys.modules['RPi.GPIO'] = GPIO
    yield GPIO
    del sys.modules['RPi']
    del sys.modules['RPi.GPIO']
