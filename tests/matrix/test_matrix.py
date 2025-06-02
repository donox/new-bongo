# tests/unit/test_matrix.py

import unittest
from bongo.matrix.basic_matrix import BasicLEDMatrix
from bongo.hardware.mock_hal import MockPixelController


class TestBasicLEDMatrix(unittest.TestCase):

    def setUp(self):
        self.rows = 3
        self.cols = 3
        self.controller = MockPixelController(self.rows, self.cols)
        self.matrix = BasicLEDMatrix()
        self.matrix.initialize(self.rows, self.cols, self.controller)

    def test_initialization_creates_grid(self):
        self.assertEqual(self.matrix.rows, self.rows)
        self.assertEqual(self.matrix.cols, self.cols)
        for r in range(self.rows):
            for c in range(self.cols):
                led = self.matrix.get_led(r, c)
                self.assertIsNotNone(led)
                self.assertEqual(led.row, r)
                self.assertEqual(led.col, c)

    def test_get_led_bounds_check(self):
        self.assertIsNone(self.matrix.get_led(-1, 0))
        self.assertIsNone(self.matrix.get_led(self.rows, 0))
        self.assertIsNone(self.matrix.get_led(0, self.cols))

    def test_fill_sets_all_leds(self):
        self.matrix.fill(255, 0, 0, brightness=0.5)
        for led in self.matrix.get_all_leds():
            self.assertEqual(led.color, (255, 0, 0))
            self.assertAlmostEqual(led.brightness, 0.5)

    def test_clear_all_turns_everything_off(self):
        self.matrix.fill(200, 200, 200, brightness=1.0)
        self.matrix.clear_all()
        for led in self.matrix.get_all_leds():
            self.assertEqual(led.color, (0, 0, 0))
            self.assertEqual(led.brightness, 0.0)

    def test_set_pixel_color_updates_hardware(self):
        self.matrix.set_pixel_color(1, 1, 100, 150, 200, 0.8)
        state = self.controller.get_pixel_state(1, 1)
        self.assertEqual(state, (100, 150, 200, 0.8))

    def test_set_frame_updates_entire_matrix(self):
        frame = [
            [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
            [(255, 255, 0), (0, 255, 255), (255, 0, 255)],
            [(100, 100, 100), (50, 50, 50), (200, 200, 200)],
        ]
        self.matrix.set_frame(frame, brightness=0.6)
        for r in range(self.rows):
            for c in range(self.cols):
                state = self.controller.get_pixel_state(r, c)
                expected = (*frame[r][c], 0.6)
                self.assertEqual(state, expected)

    def test_set_frame_invalid_dimensions(self):
        bad_frame = [[(255, 0, 0)] * 2 for _ in range(2)]  # 2x2, should be 3x3
        with self.assertRaises(ValueError):
            self.matrix.set_frame(bad_frame, brightness=1.0)

    def test_shutdown_clears_and_delegates(self):
        self.matrix.fill(255, 255, 255, brightness=1.0)
        self.matrix.shutdown()
        for r in range(self.rows):
            for c in range(self.cols):
                state = self.controller.get_pixel_state(r, c)
                self.assertEqual(state, (0, 0, 0, 0.0))


if __name__ == "__main__":
    unittest.main()
