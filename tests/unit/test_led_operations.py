import pytest
import time
from bongo.operations.led_operation import LEDPixelOperation

def test_ramp_progression():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now,
        target_brightness=1.0,
        ramp_duration=1.0,
        hold_duration=0.0,
        fade_duration=0.0
    )

    assert op.brightness_at(now) == 0.0
    assert 0.4 < op.brightness_at(now + 0.5) < 0.6
    assert op.brightness_at(now + 1.0) == 1.0

def test_fade_progression():
    now = time.monotonic()
    op = LEDOperation(
        start_time=now,
        target_brightness=1.0,
        ramp_duration=0.0,
        hold_duration=0.0,
        fade_duration=1.0
    )

    assert op.brightness_at(now) == 1.0
    assert 0.4 < op.brightness_at(now + 0.5) < 0.6
    assert op.brightness_at(now + 1.0) == 0.0

def test_hold_phase():
    now = time.monotonic()
    op = LEDPixelOperation(
        start_time=now,
        target_brightness=1.0,
        ramp_duration=0.0,
        hold_duration=1.0,
        fade_duration=0.0
    )

    assert op.brightness_at(now) == 1.0
    assert op.brightness_at(now + 0.5) == 1.0
    assert op.brightness_at(now + 1.0) == 0.0  # Operation ends after hold
