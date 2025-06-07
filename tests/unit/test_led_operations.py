# src/bongo/operations/led_operation.py
import time
from typing import Optional


class LEDPixelOperation:
    """
    Represents an operation for a single LED pixel over time,
    defining its brightness envelope (ramp, hold, fade).
    """

    def __init__(
            self,
            target_brightness: float,  # Typically 0.0 to 1.0
            ramp_duration: float,  # Seconds
            hold_duration: float,  # Seconds
            fade_duration: float,  # Seconds
            start_time: Optional[float] = None,  # Monotonic time when the operation should begin
            initial_brightness: float = 0.0  # Brightness at the very start of the operation
    ):
        """
        Initializes an LEDPixelOperation.

        Args:
            target_brightness: The peak brightness level (e.g., 1.0 for full).
            ramp_duration: Time in seconds to ramp up to target_brightness.
            hold_duration: Time in seconds to hold at target_brightness.
            fade_duration: Time in seconds to fade from target_brightness back to initial_brightness (or 0).
            start_time: The monotonic time (e.g., from time.monotonic()) when this operation
                        is scheduled to begin. If None, it might be set externally or assumed to start immediately.
            initial_brightness: The brightness level from which the ramp-up begins and to which fade-down returns.
        """
        if not (0.0 <= target_brightness <= 1.0):
            raise ValueError("Target brightness must be between 0.0 and 1.0")
        if not (0.0 <= initial_brightness <= 1.0):
            raise ValueError("Initial brightness must be between 0.0 and 1.0")
        if ramp_duration < 0 or hold_duration < 0 or fade_duration < 0:
            raise ValueError("Durations (ramp, hold, fade) cannot be negative.")

        self.start_time: Optional[float] = start_time
        self.target_brightness: float = target_brightness
        self.initial_brightness: float = initial_brightness  # Brightness before ramp and after fade

        self.ramp_duration: float = ramp_duration
        self.hold_duration: float = hold_duration
        self.fade_duration: float = fade_duration

        # Calculate offsets from the start of the operation (elapsed_time = 0)
        self.ramp_end_time_offset: float = self.ramp_duration
        self.hold_end_time_offset: float = self.ramp_duration + self.hold_duration
        self.fade_end_time_offset: float = self.ramp_duration + self.hold_duration + self.fade_duration

        self.total_duration: float = self.fade_end_time_offset  # Same as fade_end_time_offset
        self.is_active: bool = True  # Operation is considered active until it completes or is cancelled

    def get_brightness(self, current_time: float) -> float:
        """
        Calculates the brightness of the LED at the given current_time.
        Assumes current_time and start_time are from the same monotonic clock.

        Args:
            current_time: The current monotonic time.

        Returns:
            The calculated brightness (0.0 to 1.0).
        """
        if self.start_time is None:
            # Operation hasn't been placed on a timeline yet.
            return self.initial_brightness

        elapsed_time = current_time - self.start_time

        if elapsed_time < 0:  # Operation has not started yet
            return self.initial_brightness

        calculated_brightness = self.initial_brightness  # Default if no phase matches

        # Ramp-up phase: Occurs from elapsed_time 0 up to and including ramp_end_time_offset
        if elapsed_time <= self.ramp_end_time_offset:
            if self.ramp_duration > 0:
                progress = min(1.0, elapsed_time / self.ramp_duration)
                calculated_brightness = self.initial_brightness + (
                            self.target_brightness - self.initial_brightness) * progress
            else:  # ramp_duration is 0 (instant ramp)
                calculated_brightness = self.target_brightness

        # Hold phase: Occurs after ramp_end_time_offset up to and including hold_end_time_offset
        elif elapsed_time <= self.hold_end_time_offset:
            # This condition implies elapsed_time > self.ramp_end_time_offset
            if self.hold_duration > 0:  # Only if hold phase has a duration
                calculated_brightness = self.target_brightness
            else:  # hold_duration is 0
                # If hold_duration is 0, then hold_end_time_offset == ramp_end_time_offset.
                # This block is effectively skipped if hold_duration is 0, because the
                # preceding 'if' (for ramp) would have caught elapsed_time == ramp_end_time_offset.
                # If elapsed_time > ramp_end_time_offset, and hold_duration is 0,
                # calculated_brightness would carry over from the ramp phase if we fell through,
                # or be set by the fade/completion logic.
                # The critical point is that if ramp_duration is non-zero and hold_duration is zero,
                # at elapsed_time == ramp_end_time_offset, the ramp block sets target_brightness.
                # This 'pass' means if hold is zero, we don't explicitly change brightness here;
                # it's either set by ramp or will be by fade/completion.
                pass

                # Fade-down phase: Occurs after hold_end_time_offset up to (but not including) fade_end_time_offset
        elif elapsed_time < self.fade_end_time_offset:
            # This condition implies elapsed_time > self.hold_end_time_offset
            if self.fade_duration > 0:  # Only if fade phase has a duration
                time_into_fade = elapsed_time - self.hold_end_time_offset
                progress = min(1.0, time_into_fade / self.fade_duration)
                calculated_brightness = self.target_brightness - (
                            self.target_brightness - self.initial_brightness) * progress
            else:  # fade_duration is 0
                # Similar to hold_duration=0, if fade_duration is 0, this block is skipped.
                # Brightness carries from ramp/hold or is set by completion.
                pass

        # Completion: Occurs at or after fade_end_time_offset
        else:  # elapsed_time >= self.fade_end_time_offset
            self.is_active = False  # Mark as inactive
            if self.hold_duration == 0 and self.fade_duration == 0:
                # If the operation had no hold or fade defined, it implies that
                # after the ramp, it should maintain target_brightness.
                # Since elapsed_time >= fade_end_time_offset (which equals ramp_end_time_offset here),
                # it should be at target_brightness.
                calculated_brightness = self.target_brightness
            else:
                # If there was a defined hold or fade phase, completion means
                # returning to initial_brightness.
                calculated_brightness = self.initial_brightness

        return max(0.0, min(1.0, calculated_brightness))

    def is_completed(self, current_time: float) -> bool:
        """
        Checks if the operation has completed its full duration.

        Args:
            current_time: The current monotonic time.

        Returns:
            True if the operation is completed, False otherwise.
        """
        if self.start_time is None:
            return False  # Cannot determine completion without a start time
        return current_time >= (self.start_time + self.total_duration)

    def __repr__(self) -> str:
        start_time_str = f"{self.start_time:.2f}s" if self.start_time is not None else "None"
        return (
            f"LEDPixelOperation(start_time={start_time_str}, target={self.target_brightness:.2f}, "
            f"ramp={self.ramp_duration:.2f}s, hold={self.hold_duration:.2f}s, fade={self.fade_duration:.2f}s, "
            f"initial={self.initial_brightness:.2f})"
        )


# Example of a simple LEDOperation if needed by other parts (distinct from PixelOperation)
class LEDOperation:
    """
    Represents a single, direct LED operation with channel and PWM values.
    This is more for direct control rather than timed envelopes.
    """

    def __init__(self, channel: int, on_value: int, off_value: int):
        if not (0 <= channel <= 15):  # Assuming PCA9685 channels
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

