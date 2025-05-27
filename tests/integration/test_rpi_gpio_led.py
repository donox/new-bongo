import os
import sys
import time
import unittest
import pytest

print("✅ Starting test_rpi_gpio_led.py")

# Check if RPi.GPIO is available or forced for test execution
GPIO_AVAILABLE = False
try:
    import RPi.GPIO as GPIO
except ImportError as e:
    print("❌ RPi.GPIO import failed:", e)
else:
    try:
        from bongo.hardware.rpi_gpio_hal import RPiGPIOPixelController, clear_pwm_objects
        GPIO_AVAILABLE = True
    except ImportError as e:
        print("❌ RPiGPIOPixelController import failed:", e)

# Skip the entire module if GPIO not available and not forced
if not GPIO_AVAILABLE and os.getenv("FORCE_GPIO") != "1":
    pytest.skip("RPi.GPIO not available — skipping GPIO integration tests", allow_module_level=True)

from bongo.models.led import BasicLED
from bongo.matrix.basic_matrix import BasicLEDMatrix
from bongo.operations.led_operation import LEDOperation, BRIGHTNESS_MAX
from bongo.operations.animation_manager import AnimationManager

class TestPiPWMLEDIntegration(unittest.TestCase):
    """Integration tests for the RPiGPIOPixelController and LED behavior."""

    def setUp(self):
        print("\n--- Setting up RPiGPIOPixelController test ---")
        self.pins = [12]  # others could be 13, 18, 19
        self.rows = 1
        self.cols = 1

        GPIO.cleanup()
        clear_pwm_objects()

        self.controller = RPiGPIOPixelController(
            rows=self.rows,
            cols=self.cols,
            gpio_pins=self.pins
        )
        self.matrix = BasicLEDMatrix()
        self.matrix.initialize(self.rows, self.cols, self.controller)

        self.manager = AnimationManager(self.matrix, self.controller)  # ← This was missing

    def tearDown(self):
        print("--- Shutting down controller ---")
        self.manager.stop()
        self.controller.shutdown()

    def test_set_brightness_visible(self):
        self.controller.set_pixel(0, 0, 255, 255, 255, brightness=0.8)
        self.controller.show()
        state = self.controller.get_pixel_state(0, 0)
        self.assertEqual(state[0:3], (255, 255, 255))
        self.assertAlmostEqual(state[3], 0.8, places=2)

    def test_initial_state_off(self):
        state = self.controller.get_pixel_state(0, 0)
        self.assertEqual(state, (0, 0, 0, 0.0))

    def test_off_method(self):
        self.controller.set_pixel(0, 0, 255, 255, 255, brightness=1.0)
        self.controller.clear()
        state = self.controller.get_pixel_state(0, 0)
        self.assertEqual(state, (0, 0, 0, 0.0))

    def test_brightness_clamping(self):
        with self.assertRaises(ValueError):
            self.controller.set_pixel(0, 0, 255, 255, 255, brightness=1.5)

    def test_animation_ramp_and_fade(self):
        op = LEDOperation(
            start_time=time.monotonic(),
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=0.2,
            hold_duration=0.3,
            fade_duration=0.2
        )
        self.manager.add_operation(0, 0, op)
        self.manager.start()
        time.sleep(1.0)
        self.manager.stop()
        state = self.controller.get_pixel_state(0, 0)
        self.assertEqual(state, (0, 0, 0, 0.0))


if __name__ == '__main__':
    unittest.main()
