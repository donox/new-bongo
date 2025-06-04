import pytest
from bongo.matrix.matrix import LEDMatrix

class TestLEDMatrix:

    def test_initialization_creates_grid(self, mock_matrix):
        assert mock_matrix.rows == 2
        assert mock_matrix.cols == 2

    def test_get_led_bounds_check(self, mock_matrix):
        led = mock_matrix.get_led(1, 1)
        assert led is not None

    def test_set_pixel_color_updates_hardware(self, mock_matrix):
        mock_matrix.set_pixel(0, 0, 128)
        led = mock_matrix.get_led(0, 0)
        assert led.get_pixel() == 128

    def test_fill_sets_all_leds(self, mock_matrix):
        mock_matrix.fill(100)
        for led in mock_matrix.leds:
            assert led.get_pixel() == 100

    def test_clear_all_turns_everything_off(self, mock_matrix):
        mock_matrix.fill(255)
        mock_matrix.clear()
        for led in mock_matrix.leds:
            assert led.get_pixel() == 0

    def test_set_frame_updates_entire_matrix(self, mock_matrix):
        frame = [
            [100, 101],
            [102, 103]
        ]
        mock_matrix.set_frame(frame)
        assert mock_matrix.get_led(0, 0).get_pixel() == 100
        assert mock_matrix.get_led(0, 1).get_pixel() == 101
        assert mock_matrix.get_led(1, 0).get_pixel() == 102
        assert mock_matrix.get_led(1, 1).get_pixel() == 103

    def test_set_frame_invalid_dimensions(self, mock_matrix):
        frame = [[100]]  # Wrong size
        with pytest.raises(ValueError):
            mock_matrix.set_frame(frame)

    def test_shutdown_clears_and_delegates(self, mock_matrix):
        mock_matrix.fill(255)
        mock_matrix.shutdown()
        for led in mock_matrix.leds:
            assert led.get_pixel() == 0
