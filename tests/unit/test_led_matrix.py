# tests/unit/test_led_matrix.py
import pytest
from unittest.mock import MagicMock

# Assuming these are the correct paths based on your project structure
from src.bongo.controller.hybrid_controller import HybridLEDController
from src.bongo.matrix.matrix import LEDMatrix


# This test file assumes a conftest.py provides the mock_hardware_manager fixture.

@pytest.fixture
def matrix_via_config(mock_hardware_manager):
    """
    Creates an LEDMatrix instance using a 'config' list.
    This fixture is now updated to include the required 'type' key.
    """
    test_config = [
        {"row": 0, "col": 0, "type": "pca9685", "controller_address": 0x40, "led_channel": 0},
        {"row": 0, "col": 1, "type": "pca9685", "controller_address": 0x40, "led_channel": 1},
        {"row": 1, "col": 0, "type": "pca9685", "controller_address": 0x41, "led_channel": 5},
        {"row": 1, "col": 1, "type": "pca9685", "controller_address": 0x41, "led_channel": 6},
    ]

    # Initialize LEDMatrix with the config and the mock hardware manager
    matrix = LEDMatrix(config=test_config, hardware_manager=mock_hardware_manager)
    return matrix


@pytest.fixture
def matrix_via_rows_cols(mock_hardware_manager):
    """Creates an LEDMatrix instance using 'rows', 'cols', for testing."""
    # This fixture needs to be updated to match the new LEDMatrix constructor,
    # which now only takes config and hardware_manager. We can simulate a
    # rows/cols setup by generating a config on the fly.
    rows = 2
    cols = 3
    controller_address = 0x70

    test_config = []
    current_channel = 0
    for r in range(rows):
        for c in range(cols):
            test_config.append({
                "row": r, "col": c, "type": "pca9685",
                "controller_address": controller_address,
                "led_channel": current_channel
            })
            current_channel += 1

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
        assert mock_hardware_manager.get_controller.call_count == 4

        # Verify that an LED was created correctly
        led_at_0_0 = matrix.get_led(0, 0)
        assert isinstance(led_at_0_0, HybridLEDController)
        assert led_at_0_0.led_channel == 0

    def test_set_pixel_delegates_to_correct_controller(self, matrix_via_config):
        """
        Test that set_pixel correctly finds the logical LED and calls set_brightness.
        """
        matrix = matrix_via_config
        led_1_1 = matrix.get_led(1, 1)
        assert led_1_1 is not None

        # Call the method under test
        matrix.set_pixel(1, 1, 0.5)

        # Verify the mock API was called correctly.
        led_1_1.controller.set_pwm.assert_called_once()

    def test_get_led(self, matrix_via_config):
        """Test the get_led method."""
        led = matrix_via_config.get_led(1, 1)
        assert led is not None
        assert led.led_channel == 6

        assert matrix_via_config.get_led(9, 9) is None  # Out of bounds

