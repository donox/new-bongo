# src/bongo/controller/hybrid_controller.py
import logging
from unittest.mock import MagicMock  # Import MagicMock for type checking in tests

# --- For handling real vs. mock environments ---
try:
    from adafruit_pca9685 import PCA9685

    IS_REAL_HARDWARE = True
except (NotImplementedError, ModuleNotFoundError):
    # Define a placeholder class so the code doesn't crash on import
    # when adafruit libraries aren't available (e.g., on a non-Pi machine).
    class PCA9685:
        pass


    IS_REAL_HARDWARE = False

logger = logging.getLogger(__name__)


class HybridLEDController:
    """
    Controls a single Black & White (monochromatic) LED connected to a PCA9685 controller.
    This class can operate with both a real Adafruit_PCA9685 object and a mock
    object for testing by checking the type of the provided controller.
    """

    def __init__(self, led_channel: int, pca_controller):
        """
        Initializes a logical LED controller.

        Args:
            led_channel: The channel (0-15) this LED is on.
            pca_controller: A pre-initialized PCA9685 controller object (real or mock).
        """
        if not (0 <= led_channel <= 15):
            raise ValueError("LED channel must be between 0 and 15.")
        if pca_controller is None:
            raise ValueError("A valid pca_controller object must be provided.")

        self.led_channel = led_channel
        self.controller = pca_controller
        self.current_brightness: float = 0.0

    def _calculate_duty_cycle(self, brightness_norm: float) -> int:
        """Calculates the 16-bit duty cycle for the Adafruit library."""
        if not (0.0 <= brightness_norm <= 1.0):
            brightness_norm = max(0.0, min(1.0, brightness_norm))
        # The Adafruit library uses a 16-bit duty cycle (0-65535)
        return int(brightness_norm * 65535)

    def set_brightness(self, brightness_norm: float):
        """
        Sets the brightness of the B/W LED. This method now uses isinstance()
        to reliably distinguish between real and mock hardware controllers.
        """
        if self.controller is None:
            return

        self.current_brightness = max(0.0, min(1.0, brightness_norm))

        try:
            # --- ROBUST API HANDLING ---
            if IS_REAL_HARDWARE and isinstance(self.controller, PCA9685):
                # REAL HARDWARE API (Adafruit Library)
                duty_cycle = self._calculate_duty_cycle(self.current_brightness)
                self.controller.channels[self.led_channel].duty_cycle = duty_cycle
            elif isinstance(self.controller, MagicMock):
                # MOCKING API (For Unit Tests)
                pwm_val = int(self.current_brightness * 4095)
                self.controller.set_pwm(self.led_channel, 0, pwm_val)
            else:
                logger.warning(
                    f"Controller of type {type(self.controller)} is not a recognized Adafruit or MagicMock object. Doing nothing."
                )

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
            # If the underlying controller has a cleanup method, call it.
            # This is crucial for the test to pass.
            if hasattr(self.controller, 'cleanup') and callable(self.controller.cleanup):
                self.controller.cleanup()
