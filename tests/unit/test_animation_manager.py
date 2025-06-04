# tests/unit/test_animation_manager.py

import unittest
import time
from bongo.operations.animation_manager import AnimationManager
from bongo.operations.led_operation import LEDPixelOperation as LEDOperation
from bongo.utils.constants import BRIGHTNESS_MAX
from bongo.matrix.matrix import LEDMatrix
from bongo.hardware.mock_hal import MockPixelController


class TestAnimationManager(unittest.TestCase):

    def setUp(self):
        self.config = [
            {"row": 0, "col": 0, "type": "mock", "pin": 1},
            {"row": 0, "col": 1, "type": "mock", "pin": 2},
            {"row": 1, "col": 0, "type": "mock", "pin": 3},
            {"row": 1, "col": 1, "type": "mock", "pin": 4},
        ]
        self.matrix = LEDMatrix(config=self.config)
        # self.matrix.initialize(self.rows, self.cols, self.controller)
        self.manager = AnimationManager(self.matrix, pixel_controller=None)

    def test_add_operation_and_run(self):
        """Add a single LEDOperation and verify state change."""
        row, col = 0, 0
        op = LEDOperation(
            start_time=time.monotonic(),
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=0.1,
            hold_duration=0.2,
            fade_duration=0.1
        )

        self.manager.add_operation(row, col, op)
        self.manager.start()
        time.sleep(0.6)  # Allow operation to complete
        self.manager.stop()

        r, g, b, brightness = self.controller.get_brightness(row, col)
        self.assertEqual((r, g, b), (0, 0, 0))  # Should be black
        self.assertEqual(brightness, 0.0)       # Should be off

    def test_clear_pending_operations(self):
        row, col = 0, 0
        now = time.monotonic()
        op = LEDOperation(
            start_time=now + 5.0,
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=0.1,
            hold_duration=0.2,
            fade_duration=0.1
        )

        self.manager.add_operation(row, col, op)
        self.manager.clear_pending_operations()

        # Wait a short moment to let the thread reach queue.get()
        time.sleep(0.1)

        # Nothing should happen because we cleared the queue
        led = self.matrix.get_led(row, col)
        self.assertFalse(led.is_on)


if __name__ == "__main__":
    unittest.main()
