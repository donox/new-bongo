"""
abstract_led.py
Defines the AbstractLED interface that all concrete LED implementations must follow.
"""

from abc import ABC, abstractmethod

class AbstractLED(ABC):
    """
    Abstract base class for an individual LED.
    All concrete LED hardware implementations (e.g., PCA9685, Pi PWM, Mock)
    must inherit from this class and implement its abstract methods.
    """

    @abstractmethod
    def set_brightness(self, brightness: int):
        """
        Sets the brightness of the individual LED.
        Brightness is expected to be an integer between 0 (off) and 255 (full brightness).
        """
        pass

    @abstractmethod
    def get_brightness(self) -> int:
        """
        Returns the current logical brightness of the LED (0-255).
        """
        pass

    @abstractmethod
    def off(self):
        """
        Turns the LED completely off.
        """
        self.set_brightness(0)