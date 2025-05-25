"""
test_individual_led.py
Unit tests for the IndividualLED class, focusing on its command processing logic.
"""

import unittest
import time
import os
import sys
from unittest.mock import MagicMock, patch
import queue

# Ensure path adjustments are handled by run_tests.py globally.

from src.core.individual_led import IndividualLED
from src.hardware.abstract_led import AbstractLED

# Assumes src/core/led_commands.py exists now
from src.core.led_commands import LEDOperation, BRIGHTNESS_MAX, BRIGHTNESS_MIN


class TestIndividualLED(unittest.TestCase):
    def setUp(self):
        # Create a mock for the AbstractLED that IndividualLED will control
        self.mock_hw_led = MagicMock(spec=AbstractLED)
        # Mock initial state for get_brightness
        self.mock_hw_led.get_brightness.return_value = 0

        # Instantiate IndividualLED with the mocked hardware LED
        self.led = IndividualLED(self.mock_hw_led, "test_led_id")

        # Verify initial off call from IndividualLED's __init__
        self.mock_hw_led.off.assert_called_once()
        # DO NOT reset_mock() here if you want tearDown to assert off() calls across the test.
        # If you needed a clean slate for individual test assertions, you'd reset *within* each test.

    def tearDown(self):
        # Ensure the worker thread is stopped and cleaned up
        if self.led._is_running:  # Only stop if it was started during tests
            self.led.stop()

        # After stopping, 'off' should have been called on the mock hardware LED
        # (either by init, or by stop(), or by fade-off during an operation)
        self.mock_hw_led.off.assert_called()

    def test_initialization(self):
        # Thread should not be running immediately after init
        self.assertFalse(self.led._is_running)
        # self.mock_hw_led.off.assert_called_once() is done in setUp now.

    def test_add_operation_starts_thread(self):
        operation = LEDOperation(
            start_time=time.monotonic(),
            target_brightness=100,
            ramp_duration=0.1,
            hold_duration=0.1,
            fade_duration=0.1  # Fade duration > 0, so _execute_operation will animate to 0, not call off() directly
        )

        self.led.add_operation(operation)
        self.assertTrue(self.led._is_running)

        # Give the thread a moment to process the operation
        # This sleep should cover the total duration of the operation + buffer
        time.sleep(operation.ramp_duration + operation.hold_duration + operation.fade_duration + 0.1)

        # Verify that hardware LED methods were called by the worker thread
        self.mock_hw_led.set_brightness.assert_called()
        self.mock_hw_led.get_brightness.assert_called()  # Called by _animate_brightness

        # DO NOT assert off() here for this operation type, as it fades.
        # off() will be asserted in tearDown when self.led.stop() is called.

    def test_clear_pending_operations(self):
        # Add some dummy operations - this will start the thread
        op1 = LEDOperation(time.monotonic(), 50, 0, 0, 0)
        op2 = LEDOperation(time.monotonic(), 150, 0, 0, 0)
        self.led.add_operation(op1)
        self.led.add_operation(op2)

        # Give a small moment for the thread to maybe process the first item, if it starts extremely fast.
        # The primary goal is to ensure clear_pending_operations empties the queue.
        time.sleep(0.05)

        self.led.clear_pending_operations()

        # Assert that the queue is empty after clearing.
        self.assertEqual(self.led._command_queue.qsize(), 0)

    def test_get_current_brightness(self):
        # Mock a specific return value for get_brightness
        self.mock_hw_led.get_brightness.return_value = 123
        self.assertEqual(self.led.get_current_brightness(), 123)
        self.mock_hw_led.get_brightness.assert_called_once()


if __name__ == '__main__':
    # When running this test file directly, ensure path is set up for imports
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    src_directory = os.path.abspath(os.path.join(current_script_dir, os.pardir))
    if src_directory not in sys.path:
        sys.path.insert(0, src_directory)

    unittest.main(argv=sys.argv[:1])