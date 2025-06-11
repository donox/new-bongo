# src/bongo/hardware_manager.py
import logging
from typing import Dict, List

# --- For handling real vs. mock environments ---
try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    import RPi.GPIO as GPIO
    IS_PI = True
except (NotImplementedError, ModuleNotFoundError, RuntimeError):
    print("⚠️  Could not import hardware libraries. Assuming not on a Raspberry Pi.")
    class PCA9685: pass
    class GPIO:
        BCM = 0; OUT = 0
        @staticmethod
        def setmode(mode): pass
        @staticmethod
        def setup(pin, mode): pass
        @staticmethod
        def cleanup(): pass
    IS_PI = False

log = logging.getLogger("bongo.hardware_manager")

class HardwareManager:
    """
    Manages and provides access to all hardware resources, such as the I2C bus,
    PCA9685 controllers, and GPIO pins.
    """
    def __init__(self, pca_addresses: List[int], gpio_pins: List[int]):
        """
        Initializes all required hardware.

        Args:
            pca_addresses: A list of I2C addresses for all PCA9685 boards.
            gpio_pins: A list of all BCM GPIO pins to be configured for output.
        """
        log.info("Initializing HardwareManager...")
        self.i2c_bus = None
        self.controllers: Dict[int, PCA9685] = {}

        if not IS_PI:
            log.warning("Not on a Pi. Skipping real hardware setup.")
            return

        # --- Setup I2C and PCA9685 Controllers ---
        if pca_addresses:
            try:
                log.info("Initializing I2C bus for PCA9685 controllers...")
                self.i2c_bus = busio.I2C(board.SCL, board.SDA)
                for addr in pca_addresses:
                    log.debug(f"Initializing PCA9685 at address {hex(addr)}...")
                    self.controllers[addr] = PCA9685(self.i2c_bus, address=addr)
                log.info("PCA9685 controllers initialized.")
            except Exception as e:
                log.critical(f"Failed to initialize I2C hardware: {e}", exc_info=True)
                raise

        # --- Setup GPIO Pins ---
        if gpio_pins:
            try:
                log.info("Configuring GPIO pins...")
                GPIO.setmode(GPIO.BCM)
                for pin in gpio_pins:
                    log.debug(f"Setting up GPIO pin {pin} as OUT.")
                    GPIO.setup(pin, GPIO.OUT)
                log.info("GPIO pins configured.")
            except Exception as e:
                log.critical(f"Failed to configure GPIO pins: {e}", exc_info=True)
                raise

    def get_controller(self, address: int) -> PCA9685:
        """Retrieves a pre-initialized PCA9685 controller instance."""
        controller = self.controllers.get(address)
        if controller is None:
            raise ValueError(f"No PCA9685 controller found for address {hex(address)}.")
        return controller

    def cleanup(self):
        """Cleans up all hardware resources."""
        if IS_PI:
            log.info("Cleaning up GPIO resources...")
            GPIO.cleanup()
