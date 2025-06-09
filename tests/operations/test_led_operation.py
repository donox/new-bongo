# tests/operations/test_led_operation.py
import unittest
import time
import pytest
from unittest.mock import MagicMock

# Corrected imports based on the 'src/bongo/' structure
from src.bongo.operations.led_operation import LEDOperation, LEDPixelOperation
from src.bongo.controller.hybrid_controller import HybridLEDController


# --- Tests for LEDPixelOperation (pytest style) ---
# These tests are for the high-level animation envelope class.

def test_ramp_progression():
    """Test the brightness progression during the ramp-up phase."""
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now, target_brightness=1.0, initial_brightness=0.0,
        ramp_duration=1.0, hold_duration=0.0, fade_duration=0.0
    )
    assert op.get_brightness(now) == 0.0
    assert abs(op.get_brightness(now + 0.5) - 0.5) < 1e-6
    assert abs(op.get_brightness(now + 1.0) - 1.0) < 1e-6
    # For ramp-only, it should maintain target brightness after completion
    assert abs(op.get_brightness(now + 1.1) - 1.0) < 1e-6


# (Other LEDPixelOperation tests remain here)
def test_hold_progression():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now, target_brightness=0.8, initial_brightness=0.1,
        ramp_duration=0.5, hold_duration=1.0, fade_duration=0.0
    )
    assert abs(op.get_brightness(now + 1.0) - 0.8) < 1e-6
    # After a hold with zero fade, it should remain at target brightness
    assert abs(op.get_brightness(now + 1.5) - 0.8) < 1e-6


def test_fade_progression():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now, target_brightness=1.0, initial_brightness=0.0,
        ramp_duration=0.2, hold_duration=0.3, fade_duration=1.0
    )
    assert abs(op.get_brightness(now + 1.0) - 0.5) < 1e-6
    assert abs(op.get_brightness(now + 1.5) - 0.0) < 1e-6


def test_operation_completion():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now, target_brightness=1.0, initial_brightness=0.0,
        ramp_duration=0.1, hold_duration=0.1, fade_duration=0.1
    )
    assert not op.is_completed(now + 0.29)
    assert op.is_completed(now + 0.3)


def test_operation_before_start_time():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now + 1.0, target_brightness=1.0, initial_brightness=0.2,
        ramp_duration=0.5, hold_duration=0.5, fade_duration=0.5
    )
    assert abs(op.get_brightness(now) - 0.2) < 1e-6


def test_zero_duration_phases():
    now = time.monotonic()
    # Zero ramp
    op = LEDPixelOperation(
        start_time=now, target_brightness=0.7, initial_brightness=0.1,
        ramp_duration=0.0, hold_duration=0.1, fade_duration=0.1
    )
    assert abs(op.get_brightness(now) - 0.7) < 1e-6
    # Zero hold
    op = LEDPixelOperation(
        start_time=now, target_brightness=1.0, initial_brightness=0.0,
        ramp_duration=0.1, hold_duration=0.0, fade_duration=0.1
    )
    assert abs(op.get_brightness(now + 0.15) - 0.5) < 1e-6
    # Zero fade
    op = LEDPixelOperation(
        start_time=now, target_brightness=0.9, initial_brightness=0.2,
        ramp_duration=0.1, hold_duration=0.1, fade_duration=0.0
    )
    # With zero fade, it should maintain target brightness after the hold
    assert abs(op.get_brightness(now + 0.2) - 0.9) < 1e-6


def test_initial_brightness_effect():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now, target_brightness=1.0, initial_brightness=0.5,
        ramp_duration=1.0, hold_duration=1.0, fade_duration=1.0
    )
    assert abs(op.get_brightness(now + 0.5) - 0.75) < 1e-6
    assert abs(op.get_brightness(now + 2.5) - 0.75) < 1e-6


# --- Tests for LEDOperation (unittest.TestCase style) ---

class TestLEDOperation(unittest.TestCase):
    def test_led_operation_creation(self):
        op = LEDOperation(channel=1, on_value=100, off_value=200)
        self.assertEqual(op.get_values(), (1, 100, 200))

    def test_led_operation_value_validation(self):
        with self.assertRaises(ValueError):
            LEDOperation(channel=-1, on_value=0, off_value=0)
        with self.assertRaises(ValueError):
            LEDOperation(channel=0, on_value=4096, off_value=0)


# --- Tests for HybridLEDController (unittest.TestCase style) ---

class TestHybridLEDControllerBW(unittest.TestCase):
    """
    Tests for the refactored HybridLEDController class.
    """

    def setUp(self):
        """Set up for each test."""
        # Create a mock of the pre-initialized PCA9685 hardware object
        self.mock_pca_controller = MagicMock(name="MockPCA9685Instance")
        # Ensure the mock has the 'set_pwm' method our tests expect
        self.mock_pca_controller.set_pwm = MagicMock()
        self.led_channel = 5

        # Initialize HybridLEDController with the NEW signature:
        # __init__(self, led_channel, pca_controller)
        self.led_controller = HybridLEDController(
            led_channel=self.led_channel,
            pca_controller=self.mock_pca_controller
        )

    def test_initialization(self):
        """Test that the controller is stored correctly."""
        self.assertEqual(self.led_controller.led_channel, self.led_channel)
        self.assertIs(self.led_controller.controller, self.mock_pca_controller)

    def test_set_brightness_full(self):
        """Test setting LED to full brightness (1.0)."""
        # Call the method under test
        self.led_controller.set_brightness(1.0)

        # Verify that set_pwm was called on the mock hardware controller
        # with the correct channel and PWM values for "full on".
        # The new HybridLEDController calculates PWM on a 0-4095 scale for mocks.
        self.mock_pca_controller.set_pwm.assert_called_once_with(
            self.led_channel, 0, 4095
        )
        self.assertAlmostEqual(self.led_controller.current_brightness, 1.0)

    def test_turn_on(self):
        """Test the turn_on convenience method."""
        self.led_controller.turn_on()
        self.mock_pca_controller.set_pwm.assert_called_once_with(
            self.led_channel, 0, 4095
        )
        self.assertAlmostEqual(self.led_controller.current_brightness, 1.0)

    def test_duty_cycle_calculation(self):
        """Test the internal duty cycle calculation for the real hardware API."""
        # This tests the logic used for the Adafruit library.
        # Note: _calculate_duty_cycle is an internal method.
        self.assertEqual(self.led_controller._calculate_duty_cycle(0.0), 0)
        self.assertEqual(self.led_controller._calculate_duty_cycle(1.0), 65535)
        self.assertEqual(self.led_controller._calculate_duty_cycle(0.5), 32767)

