# src/bongo/controller/hybrid_controller.py
import logging
from unittest.mock import MagicMock

try:
    from adafruit_pca9685 import PCA9685
    IS_REAL_HARDWARE = True
except (NotImplementedError, ModuleNotFoundError):
    class PCA9685: pass
    IS_REAL_HARDWARE = False

logger = logging.getLogger("bongo.hybrid_controller")

class HybridLEDController:
    """
    Controls a single Black & White (monochromatic) LED connected to a PCA9685 controller.
    """
    def __init__(self, led_channel: int, pca_controller):
        if not (0 <= led_channel <= 15):
            raise ValueError("LED channel must be between 0 and 15.")
        if pca_controller is None:
            raise ValueError("A valid pca_controller object must be provided.")

        self.led_channel = led_channel
        self.controller = pca_controller
        self.current_brightness: float = 0.0

    def _calculate_duty_cycle(self, brightness_norm: float) -> int:
        if not (0.0 <= brightness_norm <= 1.0):
            brightness_norm = max(0.0, min(1.0, brightness_norm))
        return int(brightness_norm * 65535)

    def set_brightness(self, brightness_norm: float):
        if self.controller is None:
            return
        self.current_brightness = max(0.0, min(1.0, brightness_norm))
        try:
            if IS_REAL_HARDWARE and isinstance(self.controller, PCA9685):
                duty_cycle = self._calculate_duty_cycle(self.current_brightness)
                self.controller.channels[self.led_channel].duty_cycle = duty_cycle
            elif isinstance(self.controller, MagicMock):
                pwm_val = int(self.current_brightness * 4095)
                self.controller.set_pwm(self.led_channel, 0, pwm_val)
            else:
                logger.warning(f"Controller of type {type(self.controller)} is not recognized. Doing nothing.")
        except Exception as e:
            logger.error(f"Failed to set brightness for channel {self.led_channel}: {e}")

    def get_pixel(self) -> int:
        return int(round(self.current_brightness * 255))

    def turn_on(self):
        self.set_brightness(1.0)

    def turn_off(self):
        self.set_brightness(0.0)

    def cleanup(self):
        """Turns off the LED and calls cleanup on the underlying hardware controller."""
        if self.controller:
            self.turn_off()
            # --- THIS IS THE KEY FIX ---
            # If the underlying controller has a cleanup method, call it.
            if hasattr(self.controller, 'cleanup') and callable(self.controller.cleanup):
                self.controller.cleanup()
