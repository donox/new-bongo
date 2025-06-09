# tests/matrix/test_matrix.py
import pytest
from unittest.mock import MagicMock
from collections import Counter

# Adjust imports to match your project structure
from src.bongo.matrix.matrix import LEDMatrix


# This test file assumes a conftest.py provides the 'mock_matrix' fixture
# The fixture should correctly instantiate LEDMatrix with a mock pca9685_class.

class TestLEDMatrix:
    """Unit tests for the LEDMatrix class."""

    def test_matrix_initialization(self, mock_matrix):
        """Test matrix initialization from a mock config."""
        assert mock_matrix.rows == 2
        assert mock_matrix.cols == 2
        assert len(mock_matrix) == 4

    def test_get_led_retrieves_correctly(self, mock_matrix):
        """Test the get_led() method."""
        led = mock_matrix.get_led(0, 1)
        assert led is not None
        assert led.led_channel == 1  # Based on the config in conftest.py

        assert mock_matrix.get_led(5, 5) is None  # Out of bounds

    def test_set_pixel_color_updates_hardware(self, mock_matrix):
        """Test setting a single pixel's brightness."""
        mock_matrix.set_pixel(0, 0, 128)
        led = mock_matrix.get_led(0, 0)
        # Verify the state was set correctly on the controller object
        assert led.get_pixel() == 128

    def test_fill_sets_all_leds(self, mock_matrix):
        """Test that fill() sets the brightness for all LEDs."""
        mock_matrix.fill(100)
        # Iterate over the values (HybridLEDController objects) of the leds dictionary
        for led in mock_matrix.leds.values():
            assert led.get_pixel() == 100

    def test_clear_all_turns_everything_off(self, mock_matrix):
        """Test that clear() sets all LEDs to 0."""
        mock_matrix.fill(255)
        mock_matrix.clear()
        # Iterate over the values (HybridLEDController objects)
        for led in mock_matrix.leds.values():
            assert led.get_pixel() == 0

    def test_set_frame_updates_entire_matrix(self, mock_matrix):
        """Test updating the matrix from a 2D frame."""
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
        """Test that set_frame raises an error for mismatched dimensions."""
        frame = [[100]]  # Wrong size for a 2x2 matrix
        with pytest.raises(ValueError):
            mock_matrix.set_frame(frame)

    def test_shutdown_clears_and_delegates(self, mock_matrix):
        """
        Test that shutdown clears all LEDs and calls cleanup on each
        underlying hardware controller the correct number of times.
        """
        if not mock_matrix.leds:
            pytest.skip("Matrix has no LEDs to test.")

        # 1. First, determine the expected call counts for each mock controller.
        # This will create a dictionary like: {<MockPCA_0x40>: 2, <MockPCA_0x41>: 2}
        expected_counts = Counter(led.controller for led in mock_matrix.leds.values())
        unique_controllers = list(expected_counts.keys())

        # 2. Perform the actions
        mock_matrix.fill(255)
        mock_matrix.shutdown()

        # 3. Verify that each LED's brightness is now 0
        for led in mock_matrix.leds.values():
            assert led.get_pixel() == 0

        # 4. Loop through each UNIQUE mock controller and assert its call count.
        for controller, count in expected_counts.items():
            assert controller.cleanup.call_count == count

