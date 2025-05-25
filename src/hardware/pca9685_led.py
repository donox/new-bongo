"""
pca9685_led.py
Implements the AbstractLED for individual LEDs connected to a PCA9685 PWM driver.
Assumes a single PCA9685 board is initialized and passed in.
"""

import board
import busio
from adafruit_pca9685 import PCA9685

from src.hardware.abstract_led import AbstractLED

# Global PCA9685 object (or manage a list if daisy-chained)
_pca_boards = {} # Dictionary to hold PCA9685 instances by their I2C address

def get_pca9685_board(i2c_address: int = 0x40):
    """
    Initializes and returns a PCA9685 board instance for a given I2C address.
    Ensures only one instance per address.
    """
    if i2c_address not in _pca_boards:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            pca = PCA9685(i2c, address=i2c_address)
            pca.frequency = 1000  # Set PWM frequency (e.g., 1000 Hz)
            _pca_boards[i2c_address] = pca
            print(f"PCA9685 board at address 0x{i2c_address:X} initialized with frequency {pca.frequency} Hz.")
        except ValueError as e:
            raise RuntimeError(f"Could not initialize PCA9685 at address 0x{i2c_address:X}. "
                               f"Check wiring and I2C setup. Error: {e}")
    return _pca_boards[i2c_address]

class PCA9685LED(AbstractLED):
    """
    An LED controlled by a specific channel on a PCA9685 PWM driver board.
    """
    def __init__(self, led_id: str, pca_channel: int, pca_address: int = 0x40):
        print(f"Initializing PCA9685 LED.  channel:{pca_channel}.")
        if not (0 <= pca_channel <= 15):
            raise ValueError("PCA9685 channel must be between 0 and 15.")
        self.led_id = led_id
        self._pca = get_pca9685_board(pca_address)
        self._channel = pca_channel
        self._current_brightness = 0 # Stored logical brightness

        # PCA9685 uses 16-bit values (0-65535) for PWM duty cycle
        # We map our 0-255 brightness to this range.
        self._pwm_max = 0xFFFF # 65535

        print(f"PCA9685LED {self.led_id}: Initialized on channel {self._channel} at address 0x{pca_address:X}.")
        self.off() # Ensure LED is off on initialization

    def set_brightness(self, brightness: int):
        """
        Sets the brightness of the LED by setting the PWM duty cycle on its channel.
        Brightness is an integer between 0 (off) and 255 (full brightness).
        """
        # Ensure brightness is within expected range (0-255)
        brightness = max(0, min(255, brightness))
        self._current_brightness = brightness

        # Map 0-255 to 0-65535 for PCA9685
        pwm_value = int((brightness / 255) * self._pwm_max)

        # Set the PWM duty cycle for the specific channel
        # print(f"PCA9685LED {self.led_id}: Setting channel {self._channel} to PWM value {pwm_value} (brightness {brightness}).") # Debug
        self._pca.channels[self._channel].duty_cycle = pwm_value

    def get_brightness(self) -> int:
        """
        Returns the current logical brightness of the LED (0-255).
        Note: This returns the last *set* logical brightness, not the actual PWM value.
        """
        return self._current_brightness

    def off(self):
        """
        Turns the LED completely off by setting its PWM to 0.
        """
        self.set_brightness(0)