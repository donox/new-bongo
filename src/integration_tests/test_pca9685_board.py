# integration_tests/test_pca9685_board.py

import unittest
import time
import os
import sys

# Importantly, DO NOT mock adafruit_pca9685, board, busio here.
# Ensure sys.path is correctly configured by run_integration_tests.py
from src.hardware.pca9685_led import PCA9685LED, get_pca9685_board, _pca_boards
try:
    import board  # Requires circuitpython-board
    import busio  # Requires circuitpython-busio
    import adafruit_pca9685  # Requires adafruit-circuitpython-pca9685

    # Attempt to initialize I2C and PCA9685 to check availability
    try:
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        pca = adafruit_pca9685.PCA9685(i2c_bus)
        PCA9685_AVAILABLE = True
    except (ValueError, RuntimeError) as e:  # RuntimeError for no I2C device
        PCA9685_AVAILABLE = False
        print(f"PCA9685 board not found or I2C issue: {e}")

except ImportError as e:
    PCA9685_AVAILABLE = False
    print(f"Skipping PCA9685LED integration tests: CircuitPython dependencies missing: {e}")


@unittest.skipUnless(PCA9685_AVAILABLE, "PCA9685LED not available for actual hardware testing.")
class TestPCA9685LEDIntegration(unittest.TestCase):
    # Assuming LED connected to channel 0 on PCA9685
    PCA_CHANNEL = 0

    def setUp(self):
        print(f"\n--- Setting up PCA9685LED test on channel {self.PCA_CHANNEL} ---")
        # Clear the internal cache in pca9685_led.py to ensure a fresh board for each test
        _pca_boards.clear()
        self.led = PCA9685LED("test_integration_pca_led", 0)
        print(f"LED should be OFF initially on PCA9685 channel {self.PCA_CHANNEL}.")
        time.sleep(0.1)

    def tearDown(self):
        print(f"--- Tearing down PCA9685LED test on channel {self.PCA_CHANNEL} ---")
        self.led.off()
        # No specific cleanup function needed for PCA9685 as it's not global like RPi.GPIO
        print(f"LED should be OFF after tearDown on PCA9685 channel {self.PCA_CHANNEL}.")
        time.sleep(0.1)

    def test_initial_state_off(self):
        print("Test: Initial state (should be OFF)")
        self.assertEqual(self.led.get_brightness(), 0)

    def test_set_brightness_visible(self):
        print("Test: Setting brightness to 100 (should be visibly dim)")
        self.led.set_brightness(100)
        time.sleep(1)
        self.assertEqual(self.led.get_brightness(), 100)

        print("Test: Setting brightness to 255 (should be visibly bright)")
        self.led.set_brightness(255)
        time.sleep(1)
        self.assertEqual(self.led.get_brightness(), 255)

        print("Test: Setting brightness to 0 (should be OFF)")
        self.led.set_brightness(0)
        time.sleep(1)
        self.assertEqual(self.led.get_brightness(), 0)

    def test_off_method(self):
        print("Test: Setting brightness to 150, then calling off() (should turn OFF)")
        self.led.set_brightness(150)
        time.sleep(0.5)
        self.led.off()
        time.sleep(0.5)
        self.assertEqual(self.led.get_brightness(), 0)

    def test_brightness_clamping(self):
        print("Test: Setting brightness above 255 (should clamp to 255)")
        self.led.set_brightness(300)
        time.sleep(0.5)
        self.assertEqual(self.led.get_brightness(), 255)

        print("Test: Setting brightness below 0 (should clamp to 0)")
        self.led.set_brightness(-50)
        time.sleep(0.5)
        self.assertEqual(self.led.get_brightness(), 0)

    def test_individual_led_with_pca9685(self):
        print("Test: IndividualLED with PCA9685LED (should animate smoothly)")
        from src.core.individual_led import IndividualLED
        from src.core.led_commands import LEDOperation, BRIGHTNESS_MAX, BRIGHTNESS_MIN

        individual_led = IndividualLED(self.led, "complex_pca_led")  # Use the actual PCA9685LED instance

        op = LEDOperation(
            start_time=time.monotonic() + 0.5,
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=1.0,
            hold_duration=0.5,
            fade_duration=1.0
        )
        individual_led.add_operation(op)

        total_op_duration = op.ramp_duration + op.hold_duration + op.fade_duration + (op.start_time - time.monotonic())
        print(f"Waiting {total_op_duration:.2f}s for LED animation.")
        time.sleep(total_op_duration + 0.5)

        self.assertEqual(self.led.get_brightness(), BRIGHTNESS_MIN)

        individual_led.stop()
        self.assertFalse(individual_led._is_running)


# To run this file directly for debugging:
if __name__ == '__main__':
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_script_dir, os.pardir))
    src_directory = os.path.abspath(os.path.join(project_root, 'src'))
    if src_directory not in sys.path:
        sys.path.insert(0, src_directory)

    unittest.main()