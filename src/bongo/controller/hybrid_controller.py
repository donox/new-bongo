# src/bongo/controller/hybrid_controller.py
import logging

logger = logging.getLogger(__name__)


class HybridLEDController:
    """
    Controls a single Black & White (monochromatic) LED connected to a PCA9685 controller.
    Also stores its current brightness state for testing and state retrieval.
    """
    PWM_MAX_VALUE = 4095  # Max PWM value for PCA9685 (12-bit resolution)

    def __init__(self,
                 controller_address: int,
                 led_channel: int,
                 bus_number: int = 1,
                 pwm_frequency: int = 200,
                 pca9685_class=None):
        """
        Initializes the HybridLEDController.
        """
        if pca9685_class is None:
            raise ValueError("pca9685_class must be provided to HybridLEDController.")
        if not (0 <= led_channel <= 15):
            raise ValueError("LED channel must be between 0 and 15.")

        self.controller_address = controller_address
        self.led_channel = led_channel
        self.bus_number = bus_number  # Store the bus_number as an instance attribute
        self.current_brightness: float = 0.0  # Store current normalized brightness

        try:
            self.controller = pca9685_class(bus_number=self.bus_number, address=self.controller_address)
            self.controller.set_pwm_freq(pwm_frequency)
            logger.info(
                f"HybridLEDController initialized for B/W LED on PCA9685 addr {controller_address:#04x}, "
                f"channel {led_channel}."
            )
        except Exception as e:
            logger.error(f"Failed to initialize PCA9685 controller at address {controller_address:#04x}: {e}")
            self.controller = None
            raise

    def _calculate_pwm_values(self, brightness: int) -> tuple[int, int]:
        """
        Calculates PCA9685 on/off values for a given brightness (0-255).
        """
        if not (0 <= brightness <= 255):
            brightness = max(0, min(255, brightness))

        if brightness == 0:
            return 0, 0
        if brightness == 255:
            return 0, self.PWM_MAX_VALUE

        scaled_value = int((brightness / 255.0) * self.PWM_MAX_VALUE)
        return 0, min(scaled_value, self.PWM_MAX_VALUE)

    def set_brightness(self, brightness_norm: float):
        """
        Sets the brightness of the B/W LED.

        Args:
            brightness_norm: A float from 0.0 (off) to 1.0 (full brightness).
        """
        if self.controller is None:
            logger.error("Controller not initialized. Cannot set brightness.")
            return

        if not (0.0 <= brightness_norm <= 1.0):
            brightness_norm = max(0.0, min(1.0, brightness_norm))

        self.current_brightness = brightness_norm

        brightness_255_scale = int(round(self.current_brightness * 255))

        on_value, off_value = self._calculate_pwm_values(brightness_255_scale)
        try:
            self.controller.set_pwm(self.led_channel, on_value, off_value)
        except Exception as e:
            logger.error(
                f"Failed to set PWM for channel {self.led_channel} on controller {self.controller_address:#04x}: {e}")

    def get_pixel(self) -> int:
        """
        Gets the current brightness of the pixel, scaled to 0-255.
        """
        return int(round(self.current_brightness * 255))

    def turn_on(self):
        """Turns the LED to full brightness (1.0)."""
        self.set_brightness(1.0)

    def turn_off(self):
        """Turns the LED off (0.0 brightness)."""
        self.set_brightness(0.0)

    def cleanup(self):
        """Turns off the LED and calls cleanup on the underlying hardware controller."""
        if self.controller:
            self.turn_off()
            if hasattr(self.controller, 'cleanup') and callable(self.controller.cleanup):
                self.controller.cleanup()
