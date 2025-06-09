# tests/integration/test_pca9685_board.py
import pytest
import time
import os

# Correctly import LEDMatrix from its actual location in src/bongo/matrix/matrix.py
from src.bongo.matrix.matrix import LEDMatrix
# For integration tests, import the real hardware class from the hardware abstraction layer (HAL)
from src.bongo.hardware.pca9685_hal import PCA9685
from src.bongo.hardware_manager import HardwareManager

# This check will skip all tests in this file if not running on a Raspberry Pi.
IS_PI = os.path.exists('/proc/device-tree/model')


@pytest.mark.skipif(not IS_PI, reason="Requires real PCA9685 hardware on a Raspberry Pi")
class TestPCA9685Board:
    @pytest.fixture
    def real_matrix(self):
        """Fixture to create a real LEDMatrix instance for testing."""
        # Define the addresses of all PCA9685 boards to be tested.
        # This matches your future plan of having 0x40, 0x41, etc.
        controller_addresses = [0x40]  # Add more as you connect them

        # 1. Initialize the hardware first
        hw_manager = HardwareManager(addresses=controller_addresses)

        # 2. Define the LED layout configuration
        led_config = [
            {"row": 0, "col": 0, "controller_address": 0x40, "led_channel": 0},
            {"row": 0, "col": 1, "controller_address": 0x40, "led_channel": 1},
            {"row": 1, "col": 0, "controller_address": 0x40, "led_channel": 2},
            {"row": 1, "col": 1, "controller_address": 0x40, "led_channel": 3},
        ]

        # 3. Create the matrix, passing the initialized hardware manager
        matrix = LEDMatrix(config=led_config, hardware_manager=hw_manager)

        matrix.clear()
        yield matrix
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
