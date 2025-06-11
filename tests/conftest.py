# tests/conftest.py
import pytest
from unittest.mock import MagicMock

# Assuming these are the correct paths for your project structure
from src.bongo.matrix.matrix import LEDMatrix
# We will mock the HardwareManager itself for most unit/matrix tests
from src.bongo.hardware_manager import HardwareManager


@pytest.fixture
def mock_hardware_manager():
    """
    Creates a mock HardwareManager for testing purposes.
    This mock will provide mock PCA9685 controller objects when its
    get_controller method is called.
    """
    # 1. Create the main mock for the HardwareManager class
    hw_manager = MagicMock(spec=HardwareManager)

    # 2. Define a simple class to use as a strict specification for our mock.
    class MockPcaSpec:
        def set_pwm(self, channel, on, off):
            pass

        def cleanup(self):
            pass

    # 3. Create the mock controller objects using the strict spec.
    mock_pca_40 = MagicMock(spec=MockPcaSpec, name="MockPCA_0x40")
    mock_pca_41 = MagicMock(spec=MockPcaSpec, name="MockPCA_0x41")

    # We still need the mocked methods to be MagicMocks themselves for assertions.
    mock_pca_40.set_pwm = MagicMock()
    mock_pca_40.cleanup = MagicMock()
    mock_pca_41.set_pwm = MagicMock()
    mock_pca_41.cleanup = MagicMock()

    # 4. Configure the .get_controller() method on the mock manager.
    hw_manager.get_controller.side_effect = lambda addr: {
        0x40: mock_pca_40,
        0x41: mock_pca_41
    }.get(addr)

    return hw_manager


@pytest.fixture
def mock_matrix(mock_hardware_manager):
    """
    Provides a pre-configured, mocked LEDMatrix instance for tests.
    This fixture now uses the new architecture, consuming a mock_hardware_manager
    and including the required 'type' key in the config.
    """
    # This configuration defines a 2x2 matrix with controllers at 0x40 and 0x41
    config = [
        {"row": 0, "col": 0, "type": "pca9685", "controller_address": 0x40, "led_channel": 0},
        {"row": 0, "col": 1, "type": "pca9685", "controller_address": 0x40, "led_channel": 1},
        {"row": 1, "col": 0, "type": "pca9685", "controller_address": 0x41, "led_channel": 5},
        {"row": 1, "col": 1, "type": "pca9685", "controller_address": 0x41, "led_channel": 6},
    ]

    # Initialize LEDMatrix with the config and the MOCK hardware manager.
    matrix = LEDMatrix(config=config, hardware_manager=mock_hardware_manager)
    return matrix

