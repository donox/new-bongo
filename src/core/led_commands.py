"""
led_commands.py
Defines the data structures for LED commands and operations.
"""

import time
from src.bongo.utils.constants import BRIGHTNESS_MAX, BRIGHTNESS_MIN



class LEDOperation:
    """
    Represents a sequence of actions (ramp, hold, fade) for a single LED.
    This combines your t0, t1, t2, t3 concept into a single executable object.
    """

    def __init__(self,
                 start_time: float,  # Absolute time (time.monotonic()) when this operation should begin
                 target_brightness: int,  # Brightness to ramp up to and hold at
                 ramp_duration: float,  # Time in seconds to ramp from current brightness to target_brightness
                 hold_duration: float,  # Time in seconds to hold at target_brightness
                 fade_duration: float):  # Time in seconds to fade from target_brightness to off (0)

        if not all(isinstance(arg, (int, float)) for arg in
                   [start_time, target_brightness, ramp_duration, hold_duration, fade_duration]):
            raise TypeError("All LEDOperation arguments must be numeric.")
        if ramp_duration < 0 or hold_duration < 0 or fade_duration < 0:
            raise ValueError("Durations cannot be negative.")

        self.start_time = start_time
        self.target_brightness = max(BRIGHTNESS_MIN, min(BRIGHTNESS_MAX, target_brightness))
        self.ramp_duration = ramp_duration
        self.hold_duration = hold_duration
        self.fade_duration = fade_duration

    def __repr__(self):
        return (f"LEDOperation(start_time={self.start_time:.2f}, target_b={self.target_brightness}, "
                f"ramp={self.ramp_duration:.2f}s, hold={self.hold_duration:.2f}s, fade={self.fade_duration:.2f}s)")

    def get_total_duration(self) -> float:
        """Calculates the total active duration of this operation (excluding start_time delay)."""
        return self.ramp_duration + self.hold_duration + self.fade_duration