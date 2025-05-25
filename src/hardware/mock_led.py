"""
mock_led.py
Provides a mock implementation of the AbstractLED for testing purposes.
"""

from src.hardware.abstract_led import AbstractLED

class MockLED(AbstractLED):
    """
    A mock LED implementation for testing without actual hardware.
    It prints the LED state changes to the console.
    """
    def __init__(self, led_id: str):
        self.led_id = led_id
        self._current_brightness = 0
        print(f"MockLED {self.led_id}: Initialized.")

    def set_brightness(self, brightness: int):
        """
        Sets the mock LED's brightness and prints it.
        """
        # Ensure brightness is within expected range (0-255)
        self._current_brightness = max(0, min(255, brightness))
        print(f"MockLED {self.led_id}: Brightness set to {self._current_brightness}")

    def get_brightness(self) -> int:
        """
        Returns the current mock brightness.
        """
        return self._current_brightness

    def off(self):
        """
        Turns the mock LED off.
        """
        self.set_brightness(0)
        print(f"MockLED {self.led_id}: Turned OFF.")