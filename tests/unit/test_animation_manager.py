# tests/unit/test_animation_manager.py
import unittest
from unittest.mock import MagicMock
import time

# Assuming these are the correct paths based on your project structure
from src.bongo.controller.hybrid_controller import HybridLEDController
from src.bongo.operations.animation_manager import AnimationManager
from src.bongo.operations.led_operation import LEDPixelOperation


class TestAnimationManager(unittest.TestCase):
    """
    Unit tests for the AnimationManager class.
    """

    def setUp(self):
        """
        Set up for each test method.
        Creates a mock LED controller and an AnimationManager instance.
        """
        # Create mock LED controllers
        self.mock_led_controller1 = MagicMock(spec=HybridLEDController)
        self.mock_led_controller2 = MagicMock(spec=HybridLEDController)

        # Create a mock matrix object that has the properties AnimationManager needs.
        self.mock_matrix = MagicMock()

        # Mock the get_led method that AnimationManager will call on the matrix.
        self.mock_matrix.get_led = MagicMock(side_effect=lambda r, c: {
            (0, 0): self.mock_led_controller1,
            (0, 1): self.mock_led_controller2
        }.get((r, c)))

        # Per the source code: def __init__(self, matrix):
        self.animation_manager = AnimationManager(matrix=self.mock_matrix)

    def test_animation_manager_initialization(self):
        """
        Test that AnimationManager initializes correctly.
        """
        self.assertIs(self.animation_manager.matrix, self.mock_matrix)
        self.assertEqual(len(self.animation_manager.operations), 0)

    def test_add_operation_and_tick(self):
        """
        Test adding a pixel operation and advancing the animation timeline (tick).
        """
        # 1. Create the core animation envelope
        # LEDPixelOperation.__init__(self, target_brightness, ramp_duration, ...)
        pixel_op = LEDPixelOperation(
            target_brightness=1.0,
            ramp_duration=1.0,
            hold_duration=0.5,
            fade_duration=1.0,
        )

        # 2. Add the operation to the manager using the correct signature.
        # def add_operation(self, row, col, pixel_op)
        self.animation_manager.add_operation(0, 0, pixel_op)

        # 3. Verify the operation was added and start_time was set
        self.assertEqual(len(self.animation_manager.operations), 1)
        managed_op = self.animation_manager.operations[0]
        self.assertIsNotNone(managed_op.pixel_op.start_time)

        # 4. Simulate a tick of the animation manager AT THE EXACT START TIME.
        # This makes the test deterministic and removes floating point time issues.
        # def tick(self, time_now: float = None)
        self.animation_manager.tick(managed_op.pixel_op.start_time)

        # 5. Verify the full interaction
        # Assert that the matrix was asked for the correct LED
        self.mock_matrix.get_led.assert_called_once_with(0, 0)
        # Assert that the correct LED controller had its brightness set
        self.mock_led_controller1.set_brightness.assert_called_once()
        # Assert the other controller was untouched
        self.mock_led_controller2.set_brightness.assert_not_called()

        # Assert the brightness value was correct for the beginning of the operation.
        # Since we ticked at the exact start time, the value should be exactly 0.0.
        self.mock_led_controller1.set_brightness.assert_called_with(0.0)

    def test_clear_operations(self):
        """
        Test that clear_operations removes all active operations.
        """
        op1 = LEDPixelOperation(target_brightness=1.0, ramp_duration=1.0, hold_duration=1.0, fade_duration=1.0)
        op2 = LEDPixelOperation(target_brightness=0.5, ramp_duration=0.5, hold_duration=0.5, fade_duration=0.5)

        # def add_operation(self, row, col, pixel_op)
        self.animation_manager.add_operation(0, 0, op1)
        self.animation_manager.add_operation(0, 1, op2)

        self.assertEqual(len(self.animation_manager.operations), 2)

        # def clear_operations(self)
        self.animation_manager.clear_operations()

        self.assertEqual(len(self.animation_manager.operations), 0)
