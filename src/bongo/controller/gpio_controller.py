# src/bongo/controller/gpio_controller.py
import logging

# --- For handling real vs. mock environments ---
try:
    import RPi.GPIO as GPIO

    IS_REAL_HARDWARE = True
except (ImportError, RuntimeError):
    # Define a placeholder class for non-Pi environments
    class GPIO:
        BCM = 0
        OUT = 0
        HIGH = 1
        LOW = 0

        @staticmethod
        def setmode(mode): pass

        @staticmethod
        def setup(pin, mode): pass

        @staticmethod
        def output(pin, value): pass

        @staticmethod
        def cleanup(): pass


    IS_REAL_HARDWARE = False

log = logging.getLogger("bongo.gpio_controller")


class GPIOLEDController:
    """
    Controls a single LED connected directly to a Raspberry Pi GPIO pin.
    This provides a simple on/off mechanism without PWM brightness control.
    """

    def __init__(self, pin: int):
        """
        Initializes the controller for a specific GPIO pin.

        Args:
            pin: The BCM pin number the LED is connected to.
        """
        if pin is None:
            raise ValueError("A valid pin number must be provided.")

        self.pin = pin
        self.current_brightness: float = 0.0  # 0.0 for off, > 0.0 for on

        # The HardwareManager is now responsible for global GPIO setup.
        # This controller just handles the pin-specific logic.
        log.debug(f"GPIOLEDController created for pin {self.pin}")

    def set_brightness(self, brightness_norm: float):
        """
        Sets the state of the GPIO-controlled LED.
        Any brightness > 0 will turn the LED on. Brightness 0 will turn it off.

        Args:
            brightness_norm: A float from 0.0 (off) to 1.0 (on).
        """
        self.current_brightness = max(0.0, min(1.0, brightness_norm))

        # Simple on/off logic based on brightness
        output_state = GPIO.HIGH if self.current_brightness > 0 else GPIO.LOW

        try:
            log.debug(f"Setting GPIO pin {self.pin} to state {'HIGH' if output_state else 'LOW'}")
            GPIO.output(self.pin, output_state)
        except Exception as e:
            log.error(f"Failed to set state for GPIO pin {self.pin}: {e}", exc_info=True)

    def get_pixel(self) -> int:
        """Returns brightness on a 0-255 scale."""
        return 255 if self.current_brightness > 0 else 0

    def turn_on(self):
        """Turns the LED on."""
        self.set_brightness(1.0)

    def turn_off(self):
        """Turns the LED off."""
        self.set_brightness(0.0)

    def cleanup(self):
        """Turns off the LED during cleanup."""
        self.turn_off()
