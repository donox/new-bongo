import time
import pytest
from bongo.operations.led_operation import LEDOperation, BRIGHTNESS_MAX, BRIGHTNESS_MIN

def test_led_operation_initial_state():
    start = time.monotonic()
    op = LEDOperation(
        start_time=start,
        target_brightness=1.0,
        ramp_duration=0.5,
        hold_duration=1.0,
        fade_duration=0.5
    )

    assert op.start_time == start
    assert op.target_brightness == 1.0
    assert op.ramp_duration == 0.5
    assert op.hold_duration == 1.0
    assert op.fade_duration == 0.5
    assert op.total_duration == 2.0

def test_led_operation_brightness_ramp():
    start = time.monotonic()
    op = LEDOperation(start_time=start, target_brightness=1.0, ramp_duration=1.0, hold_duration=1.0, fade_duration=1.0)

    assert op.get_brightness(start) == pytest.approx(BRIGHTNESS_MIN)
    assert op.get_brightness(start + 0.5) == pytest.approx(0.5, abs=0.05)
    assert op.get_brightness(start + 1.0) == pytest.approx(BRIGHTNESS_MAX)

def test_led_operation_brightness_hold():
    start = time.monotonic()
    op = LEDOperation(start_time=start, target_brightness=0.75, ramp_duration=1.0, hold_duration=1.0, fade_duration=1.0)

    assert op.get_brightness(start + 1.5) == pytest.approx(0.75, abs=0.01)

def test_led_operation_brightness_fade():
    start = time.monotonic()
    op = LEDOperation(start_time=start, target_brightness=0.6, ramp_duration=1.0, hold_duration=1.0, fade_duration=1.0)

    # Mid fade
    brightness = op.get_brightness(start + 2.5)
    assert BRIGHTNESS_MIN < brightness < 0.6

    # End of fade
    assert op.get_brightness(start + 3.0) == pytest.approx(BRIGHTNESS_MIN)

def test_led_operation_expired():
    start = time.monotonic()
    op = LEDOperation(start_time=start, target_brightness=0.9, ramp_duration=1.0, hold_duration=1.0, fade_duration=1.0)

    assert not op.is_expired(start + 2.9)
    assert op.is_expired(start + 3.1)
