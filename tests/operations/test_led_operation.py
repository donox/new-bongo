import pytest
from bongo.matrix.matrix import LEDMatrix
from bongo.hardware.mock_hal import MockPixelController

class TestLEDPixelOperation:
    def setup_method(self):
        self.rows = 2
        self.cols = 2
        self.controller = MockPixelController(self.rows, self.cols)
        config = [
            {"row": r, "col": c, "controller": self.controller}
            for r in range(self.rows) for c in range(self.cols)
        ]
        self.matrix = LEDMatrix(config=config)

    def test_turn_on_single_pixel(self):
        self.matrix.set_pixel((0, 1), (255, 255, 255))
        assert self.controller.get_color((0, 1)) == (255, 255, 255)

    def test_turn_off_single_pixel(self):
        self.matrix.set_pixel((1, 0), (123, 45, 67))
        self.matrix.set_pixel((1, 0), (0, 0, 0))
        assert self.controller.get_color((1, 0)) == (0, 0, 0)

    def test_multiple_pixel_colors(self):
        colors = [((0, 0), (255, 0, 0)), ((0, 1), (0, 255, 0)), ((1, 0), (0, 0, 255)), ((1, 1), (255, 255, 0))]
        for pos, color in colors:
            self.matrix.set_pixel(pos, color)
        for pos, color in colors:
            assert self.controller.get_color(pos) == color
