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

    # 2. Create the distinct mock controller objects that the manager will provide.
    def create_mock_pca(name):
        """Helper to create a configured mock for a PCA controller."""
        mock = MagicMock(name=name)
        # Add the .set_pwm attribute that the test environment expects.
        mock.set_pwm = MagicMock()

        # --- THE DEFINITIVE FIX ---
        # Crucially, we now explicitly delete the .channels attribute.
        # This prevents the mock from creating it on the fly when hasattr() is called,
        # ensuring the correct code path is taken in HybridLEDController.
        try:
            del mock.channels
        except AttributeError:
            pass  # The attribute didn't exist, which is the desired state.

        return mock

    mock_pca_40 = create_mock_pca("MockPCA_0x40")
    mock_pca_41 = create_mock_pca("MockPCA_0x41")

    # 3. Configure the .get_controller() method on the mock manager.
    #    Use a side_effect to return the correct mock based on the address.
    hw_manager.get_controller.side_effect = lambda addr: {
        0x40: mock_pca_40,
        0x41: mock_pca_41
    }.get(addr)

    return hw_manager


@pytest.fixture
def mock_matrix(mock_hardware_manager):
    """
    Provides a pre-configured, mocked LEDMatrix instance for tests.
    This fixture now uses the new architecture, consuming a mock_hardware_manager.
    """
    # This configuration defines a 2x2 matrix with controllers at 0x40 and 0x41
    config = [
        {"row": 0, "col": 0, "controller_address": 0x40, "led_channel": 0},
        {"row": 0, "col": 1, "controller_address": 0x40, "led_channel": 1},
        {"row": 1, "col": 0, "controller_address": 0x41, "led_channel": 5},
        {"row": 1, "col": 1, "controller_address": 0x41, "led_channel": 6},
    ]

    # Initialize LEDMatrix with the config and the MOCK hardware manager.
    matrix = LEDMatrix(config=config, hardware_manager=mock_hardware_manager)
    return matrix

