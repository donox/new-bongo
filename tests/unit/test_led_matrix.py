# tests/unit/test_led_matrix.py
import pytest
from unittest.mock import MagicMock

# Assuming these are the correct paths for your project structure
from src.bongo.controller.hybrid_controller import HybridLEDController
from src.bongo.matrix.matrix import LEDMatrix


# We no longer need to mock the PCA9685 class here directly,
# as the hardware_manager will handle providing controller objects.


@pytest.fixture
def mock_hardware_manager():
    """
    Creates a mock HardwareManager for unit testing.
    This mock will provide mock PCA9685 controllers when its
    get_controller method is called.
    """
    hw_manager = MagicMock()

    # Create distinct mock controllers for each address used in tests
    mock_pca_40 = MagicMock(name="MockPCA_0x40")
    mock_pca_41 = MagicMock(name="MockPCA_0x41")

    # Configure the get_controller method to return the correct mock
    # based on the address it receives.
    hw_manager.get_controller.side_effect = lambda addr: {
        0x40: mock_pca_40,
        0x41: mock_pca_41
    }.get(addr)

    return hw_manager


@pytest.fixture
def matrix_via_config(mock_hardware_manager):
    """
    Creates an LEDMatrix instance using a 'config' list and the
    mock_hardware_manager, following the new architecture.
    """
    test_config = [
        {"row": 0, "col": 0, "controller_address": 0x40, "led_channel": 0},
        {"row": 0, "col": 1, "controller_address": 0x40, "led_channel": 1},
        {"row": 1, "col": 0, "controller_address": 0x41, "led_channel": 5},
        {"row": 1, "col": 1, "controller_address": 0x41, "led_channel": 6},
    ]

    # Initialize LEDMatrix with the config and the mock hardware manager
    matrix = LEDMatrix(config=test_config, hardware_manager=mock_hardware_manager)
    return matrix


class TestLEDMatrix:
    """Unit tests for the refactored LEDMatrix class."""

    def test_matrix_initialization_with_config(self, matrix_via_config, mock_hardware_manager):
        """
        Test matrix initialization using the 'config' and a hardware manager.
        """
        matrix = matrix_via_config

        assert matrix is not None
        assert matrix.rows == 2
        assert matrix.cols == 2
        assert len(matrix.leds) == 4

        # Verify the HardwareManager was used to get controllers
        # It should be called once for each unique address in the config.
        assert mock_hardware_manager.get_controller.call_count == 4
        mock_hardware_manager.get_controller.assert_any_call(0x40)
        mock_hardware_manager.get_controller.assert_any_call(0x41)

        # Verify that an LED was created correctly
        led_at_0_0 = matrix.get_led(0, 0)
        assert isinstance(led_at_0_0, HybridLEDController)
        # Check that it was given the correct mock PCA controller
        mock_pca_40 = mock_hardware_manager.get_controller(0x40)
        assert led_at_0_0.controller is mock_pca_40
        assert led_at_0_0.led_channel == 0

    def test_set_pixel_delegates_to_correct_controller(self, matrix_via_config):
        """
        Test that set_pixel correctly finds the logical LED and calls set_brightness.
        """
        matrix = matrix_via_config

        # Get the mock controller object that a specific LED should be using
        led_1_1 = matrix.get_led(1, 1)
        assert led_1_1 is not None

        # Call the method under test
        matrix.set_pixel(1, 1, 0.5)  # Brightness 0.5 (normalized)

        # Verify that set_brightness was called on the correct controller instance
        # The 'controller' attribute of the HybridLEDController is the mock PCA object.
        led_1_1.controller.set_pwm.assert_called_once()

    def test_get_led(self, matrix_via_config):
        """Test the get_led method."""
        led = matrix_via_config.get_led(1, 1)
        assert led is not None
        assert led.led_channel == 6

        assert matrix_via_config.get_led(9, 9) is None  # Out of bounds
