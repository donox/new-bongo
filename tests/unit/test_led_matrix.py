# tests/unit/test_led_matrix.py
import pytest
from unittest.mock import MagicMock

# Assuming these are the correct paths based on your project structure
from src.bongo.controller.hybrid_controller import HybridLEDController
from src.bongo.matrix.matrix import LEDMatrix
from src.bongo.hardware_manager import HardwareManager


@pytest.fixture
def mock_hardware_manager():
    """
    Creates a mock HardwareManager specifically for this test file.
    """
    hw_manager = MagicMock(spec=HardwareManager)
    mock_pca_40 = MagicMock(name="MockPCA_0x40")
    mock_pca_41 = MagicMock(name="MockPCA_0x41")
    hw_manager.get_controller.side_effect = lambda addr: {
        0x40: mock_pca_40,
        0x41: mock_pca_41
    }.get(addr)
    return hw_manager


@pytest.fixture
def matrix_via_config(mock_hardware_manager):
    """
    Creates an LEDMatrix instance using a 'config' list and the
    mock_hardware_manager, following the correct architecture.
    """
    # Note: Added "type" key to align with LEDMatrix constructor requirements
    test_config = [
        {"row": 0, "col": 0, "type": "pca9685", "controller_address": 0x40, "led_channel": 0},
        {"row": 0, "col": 1, "type": "pca9685", "controller_address": 0x40, "led_channel": 1},
        {"row": 1, "col": 0, "type": "pca9685", "controller_address": 0x41, "led_channel": 5},
    ]
    # Corrected constructor call
    matrix = LEDMatrix(test_config, mock_hardware_manager)
    return matrix


class TestLEDMatrix:
    """Unit tests for the refactored LEDMatrix class."""

    def test_matrix_initialization_with_config(self, matrix_via_config, mock_hardware_manager):
        """
        Test matrix initialization using the 'config' and a hardware manager.
        """
        matrix = matrix_via_config

        assert matrix is not None
        assert matrix.rows == 2  # max(0, 1) + 1
        assert matrix.cols == 2  # max(0, 0) + 1 -> This will be max(col) + 1
        assert len(matrix.leds) == 3

        # Verify the HardwareManager was used to get controllers
        assert mock_hardware_manager.get_controller.call_count == 3

        led_at_0_0 = matrix.get_led(0, 0)
        assert isinstance(led_at_0_0, HybridLEDController)

    def test_get_led(self, matrix_via_config):
        """Test the get_led method."""
        led = matrix_via_config.get_led(1, 0)
        assert led is not None
        assert led.led_channel == 5

        assert matrix_via_config.get_led(9, 9) is None

    def test_set_pixel_delegates_to_correct_controller(self, matrix_via_config):
        """
        Test that set_pixel correctly finds the logical LED and calls set_brightness.
        """
        led_1_0 = matrix_via_config.get_led(1, 0)
        # Configure the mock on the specific controller for this test
        led_1_0.controller.set_pwm = MagicMock()

        matrix_via_config.set_pixel(1, 0, 0.5)

        led_1_0.controller.set_pwm.assert_called_once()
