# src/bongo/operations/led_operation.py
"""
Defines the different levels of abstraction for LED operations within the Bongo framework.

Design Philosophy:
This module separates high-level animation concepts from low-level hardware commands
by providing two distinct operation classes:

1.  LEDPixelOperation (High-Level, Declarative):
    This class describes an animated effect over time (e.g., "fade in over 1 second,
    hold for 2, then fade out"). It is used by higher-level systems like the
    AnimationManager and PatternManager to define the "what" and "when" of an
    animation. It is hardware-agnostic and deals only with time and normalized
    brightness (0.0 to 1.0).

2.  LEDOperation (Low-Level, Imperative):
    This class represents a single, direct, atomic command to be sent to a hardware
    controller. It holds the precise PWM values for a specific hardware channel and
    has no concept of time or animation. It represents the "how" for the hardware.
    While primarily used in tests currently, it represents the final command format
    that a hardware abstraction layer would consume.

This separation allows for a clean architecture where animation logic can be developed
independently of the underlying hardware.
"""

import time
from typing import Optional


class LEDPixelOperation:
    """
    Represents a high-level operation for a single LED pixel over time, defining
    its brightness envelope (ramp, hold, fade). This is a hardware-agnostic
    description of an animated effect.
    """

    def __init__(
            self,
            target_brightness: float,  # Typically 0.0 to 1.0
            ramp_duration: float,  # Seconds
            hold_duration: float,  # Seconds
            fade_duration: float,  # Seconds
            start_time: Optional[float] = None,  # Monotonic time when the operation should begin
            initial_brightness: float = 0.5  # Brightness at the very start of the operation
    ):
        """
        Initializes an LEDPixelOperation.

        Args:
            target_brightness: The peak brightness level (e.g., 1.0 for full).
            ramp_duration: Time in seconds to ramp up to target_brightness.
            hold_duration: Time in seconds to hold at target_brightness.
            fade_duration: Time in seconds to fade from target_brightness back down.
            start_time: The monotonic time (e.g., from time.monotonic()) when this
                        operation is scheduled to begin.
            initial_brightness: The brightness level from which the ramp-up begins
                                and to which the fade-down returns.
        """
        if not (0.0 <= target_brightness <= 1.0):
            raise ValueError("Target brightness must be between 0.0 and 1.0")
        if not (0.0 <= initial_brightness <= 1.0):
            raise ValueError("Initial brightness must be between 0.0 and 1.0")
        if ramp_duration < 0 or hold_duration < 0 or fade_duration < 0:
            raise ValueError("Durations (ramp, hold, fade) cannot be negative.")

        self.start_time: Optional[float] = start_time
        self.target_brightness: float = target_brightness
        self.initial_brightness: float = initial_brightness

        self.ramp_duration: float = ramp_duration
        self.hold_duration: float = hold_duration
        self.fade_duration: float = fade_duration

        self.ramp_end_time_offset: float = self.ramp_duration
        self.hold_end_time_offset: float = self.ramp_duration + self.hold_duration
        self.fade_end_time_offset: float = self.ramp_duration + self.hold_duration + self.fade_duration

        self.total_duration: float = self.fade_end_time_offset
        self.is_active: bool = True

    def get_brightness(self, current_time: float) -> float:
        """
        Calculates the brightness of the LED at the given current_time based
        on the defined animation envelope.

        Args:
            current_time: The current monotonic time.

        Returns:
            The calculated brightness (0.0 to 1.0).
        """
        if self.start_time is None:
            return self.initial_brightness

        elapsed_time = current_time - self.start_time
        epsilon = 1e-9

        if elapsed_time < -epsilon:
            return self.initial_brightness

        calculated_brightness = self.initial_brightness

        if self.ramp_duration == 0 and self.hold_duration == 0 and self.fade_duration == 0:
            if elapsed_time >= -epsilon:
                calculated_brightness = self.target_brightness
                if elapsed_time > epsilon:
                    self.is_active = False
            return max(0.0, min(1.0, calculated_brightness))

        if elapsed_time >= self.fade_end_time_offset - epsilon:
            self.is_active = False
            if self.fade_duration > 0:
                calculated_brightness = self.initial_brightness
            else:
                calculated_brightness = self.target_brightness

        elif elapsed_time >= self.hold_end_time_offset - epsilon:
            if self.fade_duration > 0:
                time_into_fade = elapsed_time - self.hold_end_time_offset
                progress = min(1.0, max(0.0, time_into_fade / self.fade_duration))
                calculated_brightness = self.target_brightness - (
                            self.target_brightness - self.initial_brightness) * progress
            else:
                calculated_brightness = self.target_brightness

        elif elapsed_time >= self.ramp_end_time_offset - epsilon:
            calculated_brightness = self.target_brightness

        else:
            if self.ramp_duration > 0:
                progress = min(1.0, max(0.0, elapsed_time / self.ramp_duration))
                calculated_brightness = self.initial_brightness + (
                            self.target_brightness - self.initial_brightness) * progress
            else:
                calculated_brightness = self.target_brightness

        return max(0.0, min(1.0, calculated_brightness))

    def is_completed(self, current_time: float) -> bool:
        """Checks if the operation has completed its full duration."""
        if self.start_time is None:
            return False
        epsilon = 1e-9
        return current_time >= (self.start_time + self.total_duration - epsilon)

    def __repr__(self) -> str:
        start_time_str = f"{self.start_time:.2f}s" if self.start_time is not None else "None"
        return (
            f"LEDPixelOperation(start_time={start_time_str}, target={self.target_brightness:.2f}, "
            f"ramp={self.ramp_duration:.2f}s, hold={self.hold_duration:.2f}s, fade={self.fade_duration:.2f}s, "
            f"initial={self.initial_brightness:.2f})"
        )


class LEDOperation:
    """
    Represents a low-level, direct hardware command for a single LED channel.
    This class is a simple data container for PWM values and has no concept
    of time or animation. It represents the final command sent to a controller.
    """

    def __init__(self, channel: int, on_value: int, off_value: int):
        """
        Initializes a direct hardware operation.

        Args:
            channel: The specific hardware channel (0-15 for PCA9685).
            on_value: The PWM tick (0-4095) to turn the signal on.
            off_value: The PWM tick (0-4095) to turn the signal off.
        """
        if not (0 <= channel <= 15):
            raise ValueError("Channel must be between 0 and 15.")
        if not (0 <= on_value <= 4095):
            raise ValueError("On value must be between 0 and 4095.")
        if not (0 <= off_value <= 4095):
            raise ValueError("Off value must be between 0 and 4095.")
        self.channel = channel
        self.on_value = on_value
        self.off_value = off_value

    def get_values(self) -> tuple[int, int, int]:
        return self.channel, self.on_value, self.off_value

    def __repr__(self) -> str:
        return f"LEDOperation(channel={self.channel}, on_value={self.on_value}, off_value={self.off_value})"
