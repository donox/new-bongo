import time
import pytest
from unittest.mock import Mock
from bongo.operations.operation import LEDOperation
from bongo.operations.manager import AnimationManager
from bongo.matrix.matrix import LEDMatrix

from test_support_mock import get_matrix  # Will switch to real if USE_REAL_HARDWARE=1

@pytest.fixture
def matrix():
    return get_matrix()

def test_add_operation_and_tick(matrix):
    manager = AnimationManager(matrix)
    op = LEDOperation(
        start_time=time.monotonic(),
        target_brightness=1.0,
        ramp_duration=0.1,
        hold_duration=0.1,
        fade_duration=0.1,
    )
    manager.add_operation(0, 0, op)
    time.sleep(0.35)
    manager.tick()
    assert matrix.get_brightness(0, 0) == pytest.approx(0.0, abs=0.05)
    manager.stop()

def test_operation_fades_out(matrix):
    manager = AnimationManager(matrix)
    op = LEDOperation(
        start_time=time.monotonic(),
        target_brightness=0.8,
        ramp_duration=0.1,
        hold_duration=0.1,
        fade_duration=0.1,
    )
    manager.add_operation(0, 0, op)
    time.sleep(0.35)
    manager.tick()
    assert matrix.get_brightness(0, 0) < 0.1
    manager.stop()
