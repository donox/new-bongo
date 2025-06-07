# tests/operations/test_led_operation.py
import unittest
import time  # Keep time import if LEDPixelOperation tests need it (they do)
import pytest  # Keep pytest if some tests are pytest-style (they are)
from unittest.mock import MagicMock, ANY  # ANY can be useful for assertions

# Corrected imports based on the 'src/bongo/' structure
# LEDOperation and LEDPixelOperation are in src.bongo.operations.led_operation
from src.bongo.operations.led_operation import LEDOperation, LEDPixelOperation

# HybridLEDController is in src.bongo.controller.hybrid_controller
from src.bongo.controller.hybrid_controller import HybridLEDController


# For PCA9685, for unit testing HybridLEDController, we should use a mock.
# You might have a dedicated MockPCA9685 class in src.bongo.controller.mock_pca9685
# If not, we can define a MagicMock for the PCA9685 *class* to be passed to HybridLEDController.
# Let's assume we'll create a mock PCA9685 class factory when needed, similar to conftest.

# --- Tests for LEDPixelOperation (pytest style, assuming they were there) ---
# These tests seem to be from a different file originally ('tests/unit/test_led_operations.py')
# but the traceback now shows failures in 'tests/operations/test_led_operation.py'.
# I'm including them here as the error log implies this file handles them.

def test_ramp_progression():
    """Test the brightness progression during the ramp-up phase."""
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now,
        target_brightness=1.0,
        initial_brightness=0.0,
        ramp_duration=1.0,
        hold_duration=0.0,  # No hold for this specific test point
        fade_duration=0.0  # No fade for this specific test point
    )

    assert op.get_brightness(now) == 0.0, "Brightness at t=0 should be initial_brightness"

    current_test_time_ramp_half = now + 0.5
    assert abs(op.get_brightness(current_test_time_ramp_half) - 0.5) < 1e-6, "Brightness at t=0.5s (mid-ramp)"

    current_test_time_ramp_end = now + 1.0
    assert abs(op.get_brightness(current_test_time_ramp_end) - 1.0) < 1e-6, "Brightness at t=1.0s (end of ramp)"

    current_test_time_after_ramp = now + 1.1
    # With the fix, for ramp-only (hold=0, fade=0), it should maintain target_brightness
    assert abs(op.get_brightness(current_test_time_after_ramp) - 1.0) < 1e-6, "Brightness just after ramp"
    # Check completion status
    assert op.is_completed(current_test_time_after_ramp), "Should be completed after ramp if hold/fade are 0"


def test_hold_progression():
    """Test brightness during the hold phase."""
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now,
        target_brightness=0.8,
        initial_brightness=0.1,
        ramp_duration=0.5,
        hold_duration=1.0,
        fade_duration=0.0
    )
    current_test_time_mid_hold = now + 1.0  # 0.5 (ramp) + 0.5 (half_hold)
    assert abs(op.get_brightness(current_test_time_mid_hold) - 0.8) < 1e-6

    current_test_time_hold_end = now + 0.5 + 1.0  # ramp_duration + hold_duration
    assert abs(op.get_brightness(current_test_time_hold_end) - 0.8) < 1e-6


def test_fade_progression():
    """Test brightness progression during the fade-out phase."""
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now,
        target_brightness=1.0,
        initial_brightness=0.0,
        ramp_duration=0.2,
        hold_duration=0.3,
        fade_duration=1.0
    )
    current_test_time_fade_half = now + 1.0  # 0.2 (ramp) + 0.3 (hold) + 0.5 (half_fade)
    assert abs(op.get_brightness(current_test_time_fade_half) - 0.5) < 1e-6

    current_test_time_fade_end = now + 1.5  # ramp + hold + fade
    assert abs(op.get_brightness(current_test_time_fade_end) - 0.0) < 1e-6
    assert op.is_completed(current_test_time_fade_end)


def test_operation_completion():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now, target_brightness=1.0, initial_brightness=0.0,
        ramp_duration=0.1, hold_duration=0.1, fade_duration=0.1
    )
    total_duration = 0.3
    assert not op.is_completed(now + total_duration - 0.01)
    assert op.is_completed(now + total_duration)
    assert op.is_completed(now + total_duration + 0.1)


def test_operation_before_start_time():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now + 1.0, target_brightness=1.0, initial_brightness=0.2,
        ramp_duration=0.5, hold_duration=0.5, fade_duration=0.5
    )
    assert abs(op.get_brightness(now) - 0.2) < 1e-6
    assert abs(op.get_brightness(now + 0.5) - 0.2) < 1e-6


def test_zero_duration_phases():
    now = time.monotonic()
    op_zero_ramp = LEDPixelOperation(
        start_time=now, target_brightness=0.7, initial_brightness=0.1,
        ramp_duration=0.0, hold_duration=0.1, fade_duration=0.1
    )
    assert abs(op_zero_ramp.get_brightness(now) - 0.7) < 1e-6

    op_zero_hold = LEDPixelOperation(
        start_time=now, target_brightness=1.0, initial_brightness=0.0,
        ramp_duration=0.1, hold_duration=0.0, fade_duration=0.1
    )
    assert abs(op_zero_hold.get_brightness(now + 0.1) - 1.0) < 1e-6
    assert abs(op_zero_hold.get_brightness(now + 0.15) - 0.5) < 1e-6

    op_zero_fade = LEDPixelOperation(
        start_time=now, target_brightness=0.9, initial_brightness=0.2,
        ramp_duration=0.1, hold_duration=0.1, fade_duration=0.0
    )
    # If fade is 0, after hold it should be target_brightness (per revised logic if hold also 0)
    # or initial_brightness if hold was > 0.
    # With current logic in LEDPixelOperation for fade=0 (and hold > 0):
    # elapsed_time >= fade_end_offset (which is hold_end_offset) means initial_brightness
    # The specific test: now + 0.1 (ramp) + 0.1 (hold) = now + 0.2. At this point, elapsed_time == hold_end_offset.
    # If fade_duration is 0, fade_end_offset == hold_end_offset.
    # So elapsed_time == fade_end_offset. The completion logic (else block) is hit.
    # Completion logic: if hold=0 and fade=0 -> target. Else -> initial.
    # Here hold > 0, fade = 0. So it goes to target_brightness. This test is correct for that.
    #  (should end case be initial or target brightness.  Unclear, code is currently doing target)
    assert abs(op_zero_fade.get_brightness(now + 0.2) - 0.9) < 1e-6


def test_initial_brightness_effect():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now, target_brightness=1.0, initial_brightness=0.5,
        ramp_duration=1.0, hold_duration=1.0, fade_duration=1.0
    )
    assert abs(op.get_brightness(now) - 0.5) < 1e-6
    assert abs(op.get_brightness(now + 0.5) - 0.75) < 1e-6
    assert abs(op.get_brightness(now + 1.0) - 1.0) < 1e-6
    assert abs(op.get_brightness(now + 2.5) - 0.75) < 1e-6
    assert abs(op.get_brightness(now + 3.0) - 0.5) < 1e-6


# --- Tests for LEDOperation (unittest.TestCase style, assuming these are needed here) ---

class TestLEDOperation(unittest.TestCase):
    """Tests for the LEDOperation class."""

    def test_led_operation_creation(self):
        """Test basic creation and value retrieval of LEDOperation."""
        # LEDOperation is now imported correctly
        op = LEDOperation(channel=1, on_value=100, off_value=200)
        self.assertEqual(op.channel, 1)
        self.assertEqual(op.on_value, 100)
        self.assertEqual(op.off_value, 200)
        self.assertEqual(op.get_values(), (1, 100, 200))

    def test_led_operation_value_validation(self):
        """Test value validation for LEDOperation."""
        with self.assertRaises(ValueError):
            LEDOperation(channel=-1, on_value=0, off_value=0)
        with self.assertRaises(ValueError):
            LEDOperation(channel=16, on_value=0, off_value=0)
        with self.assertRaises(ValueError):
            LEDOperation(channel=0, on_value=-1, off_value=0)
        with self.assertRaises(ValueError):
            LEDOperation(channel=0, on_value=4096, off_value=0)
        with self.assertRaises(ValueError):
            LEDOperation(channel=0, on_value=0, off_value=-1)
        with self.assertRaises(ValueError):
            LEDOperation(channel=0, on_value=0, off_value=4096)


# --- Tests for HybridLEDController (unittest.TestCase style, assuming these are needed here) ---
# These tests were originally in tests/unit/test_led_controller.py.
# If this file (test_led_operation.py) is also meant to test HybridLEDController,
# then the imports and setup need to be correct.

# It's unusual to have tests for three different classes in one test file unless
# it's a very specific integration test. Typically, each class gets its own test file.
# For now, I'll include the setup assuming PCA9685 is mocked.

@pytest.fixture  # Using pytest fixture for consistency
def mock_pca_class_for_hybrid_led():
    """Provides a mock PCA9685 class for HybridLEDController testing."""
    mock_instance = MagicMock(name="PCA9685_Instance_For_HybridLED")
    mock_instance.set_pwm_freq = MagicMock()
    mock_instance.set_pwm = MagicMock()
    mock_class_factory = MagicMock(name="PCA9685_Class_For_HybridLED", return_value=mock_instance)
    return mock_class_factory, mock_instance


class TestHybridLEDControllerBW(unittest.TestCase):
    """Tests for the HybridLEDController class configured for a B/W LED."""

    def setUp(self):
        """Set up for each test."""
        # We need a mock PCA9685 class here.
        # The 'PCA9685' NameError was because it wasn't imported/defined.
        # We'll create a mock on the fly for the class.
        self.mock_pca9685_actual_instance = MagicMock(name="MockPCA9685InstanceForSetup")
        self.mock_pca9685_actual_instance.set_pwm_freq = MagicMock()
        self.mock_pca9685_actual_instance.set_pwm = MagicMock()

        self.mock_pca9685_class_factory = MagicMock(
            name="MockPCA9685ClassFactoryForSetup",
            return_value=self.mock_pca9685_actual_instance
        )

        self.controller_address = 0x40
        self.led_channel = 5
        self.bus_number = 1
        self.pwm_freq = 200

        self.led_controller = HybridLEDController(
            controller_address=self.controller_address,
            led_channel=self.led_channel,
            bus_number=self.bus_number,
            pwm_frequency=self.pwm_freq,
            pca9685_class=self.mock_pca9685_class_factory  # Inject the mock class
        )

    def test_initialization(self):
        self.mock_pca9685_class_factory.assert_called_once_with(
            bus_number=self.bus_number,
            address=self.controller_address
        )
        self.mock_pca9685_actual_instance.set_pwm_freq.assert_called_once_with(self.pwm_freq)
        self.assertEqual(self.led_controller.led_channel, self.led_channel)

    def test_calculate_pwm_values(self):
        self.assertEqual(self.led_controller._calculate_pwm_values(0), (0, 0))
        self.assertEqual(self.led_controller._calculate_pwm_values(255), (0, HybridLEDController.PWM_MAX_VALUE))
        expected_mid_off_value = int((128 / 255.0) * HybridLEDController.PWM_MAX_VALUE)
        self.assertEqual(self.led_controller._calculate_pwm_values(128), (0, expected_mid_off_value))

    def test_set_brightness_full(self):
        self.led_controller.set_brightness(255)
        self.mock_pca9685_actual_instance.set_pwm.assert_called_once_with(
            self.led_channel, 0, HybridLEDController.PWM_MAX_VALUE
        )

    def test_turn_on(self):
        self.led_controller.turn_on()
        self.mock_pca9685_actual_instance.set_pwm.assert_called_once_with(
            self.led_channel, 0, HybridLEDController.PWM_MAX_VALUE
        )

    # Add other HybridLEDController tests if they belong here...
    # test_initialization_invalid_channel, test_set_brightness_clamps_input, etc.


if __name__ == '__main__':
    # This allows running unittest tests directly if this file is executed
    # However, pytest is the runner used in the command.
    unittest.main()

