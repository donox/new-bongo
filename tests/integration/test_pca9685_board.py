# tests/integration/test_pca9685_board.py
import pytest
import time
import os

# Correctly import LEDMatrix from its actual location in src/bongo/matrix/matrix.py
from src.bongo.matrix.matrix import LEDMatrix
# For integration tests, import the real hardware class from the hardware abstraction layer (HAL)
from src.bongo.hardware.pca9685_hal import PCA9685

# This check will skip all tests in this file if not running on a Raspberry Pi.
IS_PI = os.path.exists('/proc/device-tree/model')


@pytest.mark.skipif(not IS_PI, reason="Requires real PCA9685 hardware on a Raspberry Pi")
class TestPCA9685Board:
    """
    Integration tests for the PCA9685 board using the LEDMatrix.
    These tests require the hardware to be connected.
    """

    @pytest.fixture
    def real_matrix(self):
        """Fixture to create a real LEDMatrix instance for testing."""
        # This configuration should match your actual hardware setup.
        # This example assumes a 2x2 matrix connected to a single PCA9685
        # controller at I2C address 0x40, using channels 0, 1, 2, and 3.
        matrix_details = {
            "controller_address": 0x40,
            "start_channel": 0,
            "bus_number": 1  # Default I2C bus for Raspberry Pi
        }

        # Initialize the matrix, providing the REAL PCA9685 class
        matrix = LEDMatrix(
            rows=2,
            cols=2,
            matrix_controller_config=matrix_details,
            default_pca9685_class=PCA9685
        )
        # Ensure matrix is cleared before each test
        matrix.clear()
        yield matrix
        # Teardown: ensure matrix is cleared after each test
        matrix.clear()

    def test_matrix_lights_up_and_clears(self, real_matrix):
        """
        Tests if filling the matrix with full brightness and then clearing it works.
        """
        print("\n--> Testing fill(1.0). All LEDs should be ON.")
        real_matrix.fill(1.0)
        time.sleep(2)  # Visual confirmation time

        led = real_matrix.get_led(0, 0)
        assert led is not None

        print("--> Testing clear(). All LEDs should be OFF.")
        real_matrix.clear()
        time.sleep(2)  # Visual confirmation

    def test_single_pixel(self, real_matrix):
        """
        Tests lighting up a single pixel.
        """
        print("\n--> Testing set_pixel(0, 1, 1.0). One LED should be ON.")
        real_matrix.set_pixel(0, 1, 1.0)  # Light up LED at (0, 1)
        time.sleep(2)

        print("--> Clearing board.")
        real_matrix.clear()
        time.sleep(1)
