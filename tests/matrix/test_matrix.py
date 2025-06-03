import pytest
from bongo.matrix.matrix import LEDMatrix
from bongo.hardware.mock_hal import MockPixelController
from bongo.config.simple import get_matrix_config

class TestLEDMatrix:
    def setup_method(self):
        config = get_matrix_config()
        self.matrix = LEDMatrix(config=config)

    def test_initialization_creates_grid(self):
        assert self.matrix.rows == 2
        assert self.matrix.cols == 2
        assert len(self.matrix.leds) == 4

    def test_get_led_bounds_check(self):
        with pytest.raises(IndexError):
            self.matrix.get_led(99, 99)

    def test_set_pixel_color_updates_hardware(self):
        self.matrix.set_pixel(0, 0, (255, 0, 0))
        assert self.matrix.get_led(0, 0).get_color() == (255, 0, 0)

    def test_fill_sets_all_leds(self):
        self.matrix.fill((0, 255, 0))
        for led in self.matrix.leds:
            assert led.get_color() == (0, 255, 0)

    def test_clear_all_turns_everything_off(self):
        self.matrix.fill((255, 255, 255))
        self.matrix.clear()
        for led in self.matrix.leds:
            assert led.get_color() == (0, 0, 0)

    def test_set_frame_updates_entire_matrix(self):
        frame = [[(10, 20, 30) for _ in range(self.matrix.cols)] for _ in range(self.matrix.rows)]
        self.matrix.set_frame(frame)
        for r in range(self.matrix.rows):
            for c in range(self.matrix.cols):
                assert self.matrix.get_led(r, c).get_color() == (10, 20, 30)

    def test_set_frame_invalid_dimensions(self):
        invalid_frame = [[(0, 0, 0)]]  # Too small
        with pytest.raises(ValueError):
            self.matrix.set_frame(invalid_frame)

    def test_shutdown_clears_and_delegates(self):
        self.matrix.fill((100, 100, 100))
        self.matrix.shutdown()
        for led in self.matrix.leds:
            assert led.get_color() == (0, 0, 0)
        for led in self.matrix.leds:
            assert led.controller.shutdown_called
