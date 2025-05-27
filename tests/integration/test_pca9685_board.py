import unittest
import time
from bongo.hardware.pca9685_hal import PCA9685PixelController, clear_pca9685_cache
from bongo.matrix.basic_matrix import BasicLEDMatrix
from bongo.operations.animation_manager import AnimationManager
from bongo.operations.led_operation import LEDOperation, BRIGHTNESS_MAX

class TestPCA9685PixelController(unittest.TestCase):
    """
    Integration tests for PCA9685PixelController with real hardware.
    NOTE: Ensure I2C and the board are correctly wired before running.
    """

    def setUp(self):
        print("\n--- Setting up PCA9685PixelController test ---")
        clear_pca9685_cache()

        self.rows = 1
        self.cols = 1
        self.controller = PCA9685PixelController(
            rows=self.rows,
            cols=self.cols,
            i2c_address=0x40
        )
        self.matrix = BasicLEDMatrix()
        self.matrix.initialize(self.rows, self.cols, self.controller)
        self.manager = AnimationManager(self.matrix, self.controller)

    def tearDown(self):
        print("--- Shutting down controller ---")
        self.manager.stop()
        self.controller.shutdown()

    def test_initial_state_off(self):
        state = self.controller.get_pixel_state(0, 0)
        self.assertEqual(state, (0, 0, 0, 0.0))

    def test_set_brightness_visible(self):
        self.controller.set_pixel(0, 0, 255, 255, 255, brightness=0.8)
        self.controller.show()
        state = self.controller.get_pixel_state(0, 0)
        self.assertEqual(state, (255, 255, 255, 0.8))

    def test_off_method(self):
        self.controller.set_pixel(0, 0, 255, 255, 255, brightness=1.0)
        self.controller.clear()
        state = self.controller.get_pixel_state(0, 0)
        self.assertEqual(state, (0, 0, 0, 0.0))

    def test_brightness_clamping(self):
        with self.assertRaises(ValueError):
            self.controller.set_pixel(0, 0, 255, 255, 255, brightness=1.5)
        with self.assertRaises(ValueError):
            self.controller.set_pixel(0, 0, 255, 255, 255, brightness=-0.1)

    def test_animation_ramp_and_fade(self):
        """Verify LED ramps up and down using AnimationManager."""
        op = LEDOperation(
            start_time=time.monotonic(),
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=0.2,
            hold_duration=0.3,
            fade_duration=0.2
        )
        self.manager.add_operation(0, 0, op)
        self.manager.start()
        time.sleep(1.0)  # Wait for animation to complete
        final_state = self.controller.get_pixel_state(0, 0)
        self.assertEqual(final_state, (0, 0, 0, 0.0))  # Should return to off


if __name__ == "__main__":
    unittest.main()
