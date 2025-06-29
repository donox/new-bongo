# src/bongo/operations/animation_manager.py
import time
from typing import List

# Import LEDPixelOperation, as it's the data object we'll be managing.
from .led_operation import LEDPixelOperation


class _ManagedOperation:
    """
    An internal wrapper class for managing a single active LEDPixelOperation.

    This class binds a time-based LEDPixelOperation to a specific coordinate
    on the matrix and provides the .update() method that the AnimationManager's
    tick() loop requires.

    It is assumed that this class has a narrow responsibility and will only be
    instantiated by the AnimationManager. If other parts of the application
    need to create or interact with this object directly in the future,
    its design and location should be re-evaluated, potentially promoting it
    to a standalone module.
    """

    def __init__(self, row: int, col: int, pixel_op: LEDPixelOperation, matrix):
        self.row = row
        self.col = col
        self.pixel_op = pixel_op
        self.matrix = matrix
        # Set the start time on the underlying pixel operation when it's
        # officially managed and added to the timeline.
        if self.pixel_op.start_time is None:
            self.pixel_op.start_time = time.monotonic()

    def update(self, time_now: float) -> bool:
        """
        Updates the associated LED's brightness based on the current time.

        This method performs the core logic of the animation loop for one pixel:
        1. Calculates the desired brightness from the LEDPixelOperation.
        2. Retrieves the specific LED controller from the matrix.
        3. Sets the brightness on that hardware controller.

        Args:
            time_now: The current monotonic time.

        Returns:
            True if the underlying LEDPixelOperation has completed, False otherwise.
        """
        # 1. Calculate the desired brightness
        brightness = self.pixel_op.get_brightness(time_now)

        # 2. Get the specific LED controller
        led = self.matrix.get_led(self.row, self.col)

        # 3. Set the brightness on the hardware controller
        if led:
            led.set_brightness(brightness)
            # print(f"DEBUG: Set LED ({self.row},{self.col}) brightness to {brightness:.3f}")   # !!!!!!!!!!
        else:
            print(f"ERROR: No LED found at ({self.row},{self.col})")                        # !!!!!!!!!!

        # 4. Return whether the operation is completed
        return self.pixel_op.is_completed(time_now)


class AnimationManager:
    """Manages and executes multiple LED operations over time on an LED matrix."""

    def __init__(self, matrix):
        """
        Initializes the AnimationManager.

        Args:
            matrix: An LEDMatrix instance (or a compatible mock) that the manager
                    will control.
        """
        self.matrix = matrix
        self.operations: List[_ManagedOperation] = []

    def add_operation(self, row: int, col: int, pixel_op: LEDPixelOperation):
        """
        Adds a new LED animation to be managed.

        This method takes the animation details (a LEDPixelOperation) and the
        target coordinates, wraps them in a _ManagedOperation object, and adds
        it to the active operations list.

        Args:
            row: The row of the target LED.
            col: The column of the target LED.
            pixel_op: The LEDPixelOperation describing the animation.
        """
        managed_op = _ManagedOperation(row, col, pixel_op, self.matrix)
        self.operations.append(managed_op)

    def tick(self, time_now: float = None):
        """
        Advances the animation timeline by one step.

        This method should be called repeatedly in the main application loop.
        It iterates through all active operations, updates their corresponding
        LED's brightness, and removes any operations that have completed.

        Args:
            time_now: The current monotonic time. If None, time.monotonic() will be used.
        """
        if time_now is None:
            time_now = time.monotonic()

        # Iterate over a copy of the list to safely remove items
        for op in self.operations[:]:
            done = op.update(time_now)
            if done:
                self.operations.remove(op)

    def clear_operations(self):
        """Removes all active operations from the manager."""
        self.operations.clear()
