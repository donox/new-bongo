# tests/operations/test_operations_manager.py
import pytest
from unittest.mock import MagicMock

# Assuming these are the correct paths for your project
from src.bongo.operations.animation_manager import AnimationManager
from src.bongo.operations.led_operation import LEDPixelOperation
from src.bongo.controller.hybrid_controller import HybridLEDController


@pytest.fixture
def manager():
    """
    Provides an AnimationManager instance initialized with a pure MagicMock
    for the matrix, suitable for unit testing the manager in isolation.
    """
    # For unit testing AnimationManager, we mock its dependency (the matrix).
    mock_matrix = MagicMock()
    # Configure the get_led method on the mock_matrix itself.
    mock_matrix.get_led = MagicMock()

    return AnimationManager(matrix=mock_matrix)


def test_add_operation_and_tick(manager):
    """
    Tests that adding an operation and ticking the manager correctly calls
    the underlying LED controller.
    """
    pixel_op = LEDPixelOperation(
        target_brightness=0.5,
        ramp_duration=1.0, hold_duration=1.0, fade_duration=1.0
    )

    # We need to define what the mocked get_led method returns for this test.
    mock_led = MagicMock(spec=HybridLEDController)
    manager.matrix.get_led.return_value = mock_led

    # Signature: def add_operation(self, row, col, pixel_op)
    manager.add_operation(0, 0, pixel_op)
    assert len(manager.operations) == 1

    # Signature: def tick(self, time_now: float = None)
    manager.tick()

    # Verify that the manager tried to get the correct LED from the matrix.
    manager.matrix.get_led.assert_called_once_with(0, 0)

    # Verify that the manager updated the LED's brightness.
    mock_led.set_brightness.assert_called_once()


def test_clear_operations(manager):
    """
    Tests that clear_operations correctly empties the operations list.
    """
    pixel_op = LEDPixelOperation(target_brightness=1.0, ramp_duration=0, hold_duration=0, fade_duration=0)

    # Configure the mock for this test's needs
    manager.matrix.get_led.return_value = MagicMock(spec=HybridLEDController)

    # Signature: def add_operation(self, row, col, pixel_op)
    manager.add_operation(0, 0, pixel_op)
    assert len(manager.operations) == 1

    # Signature: def clear_operations(self)
    manager.clear_operations()
    assert len(manager.operations) == 0

    # Tick again to ensure no calls are made after clearing
    manager.matrix.get_led.return_value.set_brightness.reset_mock()
    manager.tick()
    manager.matrix.get_led.return_value.set_brightness.assert_not_called()


def test_multiple_operations_called(manager):
    """
    Tests that tick() updates all active operations.
    """
    # Setup multiple mock LEDs for clarity
    mock_led1 = MagicMock(spec=HybridLEDController)
    mock_led2 = MagicMock(spec=HybridLEDController)
    # Configure the side_effect for the get_led mock for this specific test
    manager.matrix.get_led.side_effect = lambda r, c: {(0, 0): mock_led1, (1, 1): mock_led2}.get((r, c))

    op1 = LEDPixelOperation(target_brightness=1.0, ramp_duration=1, hold_duration=1, fade_duration=1)
    op2 = LEDPixelOperation(target_brightness=0.5, ramp_duration=1, hold_duration=1, fade_duration=1)

    # Add two separate operations
    manager.add_operation(0, 0, op1)
    manager.add_operation(1, 1, op2)

    # Tick the manager
    manager.tick()

    # Verify both underlying LEDs were updated
    mock_led1.set_brightness.assert_called_once()
    mock_led2.set_brightness.assert_called_once()

