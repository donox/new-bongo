# src/bongo/patterns/pattern_orchestrator.py
import time
from typing import List, Tuple, Callable
from bongo.operations.led_operation import LEDPixelOperation
from bongo.operations.animation_manager import AnimationManager


class PatternOrchestrator:
    """
    Manages complex patterns composed of multiple sub-patterns.
    """

    def __init__(self, animation_manager: AnimationManager):
        self.animation_manager = animation_manager

    def load_pattern(self, pattern_operations: List[Tuple[Tuple[int, int], LEDPixelOperation]]):
        """Load a pattern (simple or composed) into the animation manager."""
        for coords, pixel_op in pattern_operations:
            self.animation_manager.add_operation(coords[0], coords[1], pixel_op)

    def create_repeating_pattern(self,
                                 pattern_func: Callable,
                                 pattern_args: dict,
                                 repeat_count: int = 10,
                                 gap_duration: float = 0.5) -> List[Tuple[Tuple[int, int], LEDPixelOperation]]:
        """
        Create a pattern that repeats multiple times.

        Args:
            pattern_func: The pattern function to repeat (e.g., create_chase_pattern)
            pattern_args: Arguments to pass to the pattern function
            repeat_count: How many times to repeat (use large number for "forever")
            gap_duration: Time gap between repetitions
        """
        all_operations = []
        current_start_time = time.monotonic() + 0.5  # Start in 0.5 seconds

        for repeat in range(repeat_count):
            # Set the start time for this repetition
            pattern_args_copy = pattern_args.copy()  # Don't modify original args
            pattern_args_copy['start_time_base'] = current_start_time

            # Generate the pattern operations
            pattern_ops = pattern_func(**pattern_args_copy)
            all_operations.extend(pattern_ops)

            # Calculate when the next repetition should start
            if pattern_ops:
                # Find the end time of the last operation in this pattern
                max_end_time = max(
                    op[1].start_time + op[1].total_duration
                    for op in pattern_ops if op[1].start_time is not None
                )
                current_start_time = max_end_time + gap_duration

        return all_operations

    def compose_sequential(self,
                           patterns: List[Callable],
                           pattern_args: List[dict],
                           gap_duration: float = 0.0) -> List[Tuple[Tuple[int, int], LEDPixelOperation]]:
        """
        Compose multiple patterns to run sequentially.
        """
        composed_operations = []
        current_start_time = time.monotonic() + 0.5  # Start in 0.5 seconds

        for pattern_func, args in zip(patterns, pattern_args):
            # Set the start time for this pattern
            args_copy = args.copy()  # Don't modify original args
            args_copy['start_time_base'] = current_start_time

            # Generate the pattern operations
            pattern_ops = pattern_func(**args_copy)
            composed_operations.extend(pattern_ops)

            # Calculate the end time of this pattern for the next one
            if pattern_ops:
                max_end_time = max(
                    op[1].start_time + op[1].total_duration
                    for op in pattern_ops if op[1].start_time is not None
                )
                current_start_time = max_end_time + gap_duration

        return composed_operations

    def compose_layered(self,
                        patterns: List[Callable],
                        pattern_args: List[dict]) -> List[Tuple[Tuple[int, int], LEDPixelOperation]]:
        """
        Compose multiple patterns to run simultaneously (layered).
        Note: This requires careful coordination to avoid LED conflicts.
        """
        composed_operations = []
        base_time = time.monotonic() + 0.5  # Start in 0.5 seconds

        for pattern_func, args in zip(patterns, pattern_args):
            args_copy = args.copy()  # Don't modify original args
            args_copy['start_time_base'] = base_time
            pattern_ops = pattern_func(**args_copy)
            composed_operations.extend(pattern_ops)

        return composed_operations