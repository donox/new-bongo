# test_led_operation.py
import time
import unittest
from unittest.mock import Mock

from bongo.operations.led_operation import LEDOperation, BRIGHTNESS_MAX


class TestLEDOperation(unittest.TestCase):
    def test_get_brightness_ramp_up(self):
        op = LEDOperation(
            start_time=0,
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=1.0,
            hold_duration=0.0,
            fade_duration=0.0,
            controller=None
        )
        self.assertEqual(op.get_brightness(0.0), 0.0)
        self.assertEqual(op.get_brightness(0.5), BRIGHTNESS_MAX * 0.5)
        self.assertEqual(op.get_brightness(1.0), BRIGHTNESS_MAX)

    def test_update_calls_controller(self):
        mock_controller = Mock()
        op = LEDOperation(
            start_time=0.0,
            target_brightness=255,
            ramp_duration=0.5,
            hold_duration=0.0,
            fade_duration=0.0,
            controller=mock_controller
        )
        op.update(0.25)
        mock_controller.set_brightness.assert_called_once()

    def test_expired_operation(self):
        op = LEDOperation(
            start_time=0.0,
            target_brightness=255,
            ramp_duration=0.1,
            hold_duration=0.1,
            fade_duration=0.1,
            controller=None
        )
        self.assertFalse(op.is_expired(0.2))
        self.assertTrue(op.is_expired(0.4))