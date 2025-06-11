# tests/unit/test_led_matrix.py
import pytest
from unittest.mock import MagicMock

# Assuming these are the correct paths based on your project structure
from src.bongo.controller.hybrid_controller import HybridLEDController
from src.bongo.matrix.matrix import LEDMatrix


# This test file assumes a conftest.py provides the fixtures.
# The fixtures should correctly instantiate LEDMatrix with a mock pca9685_class.

@pytest.fixture
def mock_pca9685_class_with_instance():
    """
    Provides a MagicMock that simulates the PCA9685 class.
    When this mock class is instantiated, it returns another mock (the instance mock).
    Returns a tuple: (mock_class, mock_instance_returned_by_class)
    """
    mock_pca_instance = MagicMock(name="MockPCA9685_Instance")
    mock_class_factory = MagicMock(name="MockPCA9685_ClassFactory", return_value=mock_pca_instance)
    return mock_class_factory, mock_pca_instance


@pytest.fixture
def matrix_via_config(mock_pca9685_class_with_instance):
    """Creates an LEDMatrix instance using a detailed 'config' list."""
    pca_class_factory, _ = mock_pca9685_class_with_instance
    test_config = [
        {"row": 0, "col": 0, "controller_address": 0x40, "led_channel": 0},
        {"row": 0, "col": 1, "controller_address": 0x40, "led_channel": 1, "bus_number": 2},
        {"row": 1, "col": 0, "controller_address": 0x41, "led_channel": 5},
        {"row": 1, "col": 1, "controller_address": 0x41, "led_channel": 6, "pwm_frequency": 100},
    ]
    matrix = LEDMatrix(config=test_config, default_pca9685_class=pca_class_factory)
    return matrix


@pytest.fixture
def matrix_via_rows_cols(mock_pca9685_class_with_instance):
    """Creates an LEDMatrix instance using 'rows', 'cols', and 'matrix_controller_config'."""
    pca_class_factory, _ = mock_pca9685_class_with_instance
    rows = 2
    cols = 3
    controller_details = {
        "controller_address": 0x70,
        "start_channel": 0,
        "bus_number": 1,
        "pwm_frequency": 240
    }
    matrix = LEDMatrix(rows=rows, cols=cols,
                       matrix_controller_config=controller_details,
                       default_pca9685_class=pca_class_factory)
    return matrix


class TestLEDMatrix:
    """Unit tests for the LEDMatrix class."""

    def test_matrix_initialization_with_config(self, matrix_via_config):
        """Test matrix initialization using the 'config' parameter."""
        matrix = matrix_via_config

        assert matrix is not None
        assert matrix.rows == 2
        assert matrix.cols == 2
        assert len(matrix.leds) == 4

        # Correctly access the dictionary using a (row, col) tuple key
        led_at_0_0 = matrix.leds.get((0, 0))
        assert led_at_0_0 is not None
        assert isinstance(led_at_0_0, HybridLEDController)

        # Check properties of a specific created LED
        led_at_0_1 = matrix.get_led(0, 1)
        assert led_at_0_1.bus_number == 2  # This was overridden in the config

    def test_matrix_initialization_with_rows_cols(self, matrix_via_rows_cols):
        """Test matrix initialization using 'rows', 'cols'."""
        matrix = matrix_via_rows_cols

        assert matrix is not None
        assert matrix.rows == 2
        assert matrix.cols == 3
        assert len(matrix.leds) == 6

        led_at_1_2 = matrix.get_led(1, 2)
        assert isinstance(led_at_1_2, HybridLEDController)
        assert led_at_1_2.controller_address == 0x70
        assert led_at_1_2.led_channel == 5  # Channels are sequential from 0

    def test_get_led(self, matrix_via_config):
        """Test the get_led method."""
        led = matrix_via_config.get_led(1, 1)
        assert led is not None
        assert led.controller_address == 0x41
        assert led.led_channel == 6

        assert matrix_via_config.get_led(9, 9) is None  # Out of bounds

