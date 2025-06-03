from dataclasses import dataclass, field
from typing import Optional

BRIGHTNESS_MAX = 255
BRIGHTNESS_MIN = 0


@dataclass
class LEDOperation:
    start_time: float
    target_brightness: int  # 0–255
    ramp_duration: float
    hold_duration: float
    fade_duration: float
    controller: Optional[object] = field(default=None)  # The LED controller to update

    _last_brightness: float = field(default=0.0, init=False)

    @property
    def total_duration(self) -> float:
        return self.ramp_duration + self.hold_duration + self.fade_duration

    def get_brightness(self, timestamp: float) -> float:
        elapsed = timestamp - self.start_time
        if elapsed < 0:
            return 0.0  # Not started

        if elapsed <= self.ramp_duration:
            progress = elapsed / self.ramp_duration if self.ramp_duration > 0 else 1.0
            return self.target_brightness * progress

        elif elapsed <= self.ramp_duration + self.hold_duration:
            return float(self.target_brightness)

        elif elapsed <= self.total_duration:
            fade_elapsed = elapsed - self.ramp_duration - self.hold_duration
            progress = 1.0 - (fade_elapsed / self.fade_duration if self.fade_duration > 0 else 1.0)
            return self.target_brightness * progress

        else:
            return 0.0  # Fully faded

    def update(self, timestamp: float):
        brightness = self.get_brightness(timestamp)
        self._last_brightness = brightness

        if self.controller:
            self.controller.set_brightness(brightness)

    def is_expired(self, timestamp: float) -> bool:
        return timestamp >= self.start_time + self.total_duration

    def get_last_brightness(self) -> float:
        return self._last_brightness
