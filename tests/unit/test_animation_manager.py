# test_animation_manager.py
import time
import unittest
from unittest.mock import Mock

from bongo.controller.hybrid_controller import HybridLEDController
from bongo.matrix.matrix import LEDMatrix
from bongo.operations.animation_manager import AnimationManager

class TestAnimationManager(unittest.TestCase):
    def setUp(self):
        self.config = [
            {"row": 0, "col": 0, "type": "mock", "pin": 1},
            {"row": 0, "col": 1, "type": "mock", "pin": 2},
            {"row": 1, "col": 0, "type": "mock", "pin": 3},
            {"row": 1, "col": 1, "type": "mock", "pin": 4},
        ]
        self.controller = HybridLEDController(rows=2, cols=2)
        self.matrix = LEDMatrix(config=self.config)
        self.manager = AnimationManager(self.matrix, self.controller)


    def test_add_operation_and_run(self):
        op = LEDOperation(
            start_time=time.monotonic(),
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=0.1,
            hold_duration=0.2,
            fade_duration=0.1,
            controller=self.matrix.leds[0]
        )
        self.manager.add_operation(op)
        self.manager.tick()
        self.assertTrue(op.get_last_brightness() > 0)