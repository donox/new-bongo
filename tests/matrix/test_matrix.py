import pytest
from bongo.matrix.matrix import LEDMatrix
from bongo.hardware.mock_hal import MockPixelController

class TestLEDMatrix:
    def setup_method(self):
        self.rows = 3
        self.cols = 3
        self.controller = MockPixelController(self.rows, self.cols)
        config = [
            {"row": r, "col": c, "controller": self.controller}
            for r in range(self.rows) for c in range(self.cols)
        ]
        self.matrix = LEDMatrix(config=config)

    def test_initialization_creates_grid(self):
        assert self.matrix.rows == 3
        assert self.matrix.cols == 3
        assert len(self.matrix.leds) == 9

    def test_get_led_bounds_check(self):
        assert self.matrix.get_led((0, 0)) is not None
        with pytest.raises(IndexError):
            self.matrix.get_led((10, 10))

    def test_set_pixel_color_updates_hardware(self):
        self.matrix.set_pixel((1, 1), (255, 0, 0))
        assert self.controller.get_color((1, 1)) == (255, 0, 0)

    def test_fill_sets_all_leds(self):
        self.matrix.fill((0, 255, 0))
        for r in range(self.rows):
            for c in range(self.cols):
                assert self.controller.get_color((r, c)) == (0, 255, 0)

    def test_clear_all_turns_everything_off(self):
        self.matrix.fill((123, 123, 123))
        self.matrix.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                assert self.controller.get_color((r, c)) == (0, 0, 0)

    def test_set_frame_updates_entire_matrix(self):
        frame = [[(10, 20, 30) for _ in range(self.cols)] for _ in range(self.rows)]
        self.matrix.set_frame(frame)
        for r in range(self.rows):
            for c in range(self.cols):
                assert self.controller.get_color((r, c)) == (10, 20, 30)

    def test_set_frame_invalid_dimensions(self):
        frame = [[(1, 2, 3)] * (self.cols + 1)] * self.rows
        with pytest.raises(ValueError):
            self.matrix.set_frame(frame)

    def test_shutdown_clears_and_delegates(self):
        self.matrix.fill((111, 111, 111))
        self.matrix.shutdown()
        for r in range(self.rows):
            for c in range(self.cols):
                assert self.controller.get_color((r, c)) == (0, 0, 0)
