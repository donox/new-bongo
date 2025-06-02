from dataclasses import dataclass


# Brightness scale constants (can be moved to bongo/utils/constants.py if needed)
BRIGHTNESS_MAX = 255
BRIGHTNESS_MIN = 0


@dataclass
class LEDOperation:
    """
    Represents a time-based lighting operation for a single LED.
    Used by AnimationManager to animate transitions.
    """
    start_time: float  # Time to begin this operation (monotonic)
    target_brightness: int  # 0–255
    ramp_duration: float  # Time to ramp up (seconds)
    hold_duration: float  # Time to hold brightness (seconds)
    fade_duration: float  # Time to fade back down (seconds)

    @property
    def total_duration(self):
        return self.ramp_duration + self.hold_duration + self.fade_duration

    def get_brightness(self, timestamp: float) -> float:
        # logic for ramp → hold → fade
        ...

    def is_expired(self, timestamp: float) -> bool:
        return timestamp >= self.start_time + self.total_duration


