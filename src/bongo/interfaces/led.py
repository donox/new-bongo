# new-bongo/src/bongo/interfaces/led.py

from abc import ABC, abstractmethod
from typing import Tuple

class ILED(ABC):
    """
    Interface for a single conceptual LED within the system.
    This defines how we interact with a logical LED, abstracting away
    its physical implementation or exact location on a matrix.
    """

    @property
    @abstractmethod
    def row(self) -> int:
        """The row coordinate of the LED in a matrix."""
        pass

    @property
    @abstractmethod
    def col(self) -> int:
        """The column coordinate of the LED in a matrix."""
        pass

    @property
    @abstractmethod
    def color(self) -> Tuple[int, int, int]:
        """
        The current color of the LED as an RGB tuple (0-255 for each component).
        """
        pass

    @color.setter
    @abstractmethod
    def color(self, rgb: Tuple[int, int, int]) -> None:
        """
        Sets the color of the LED.
        :param rgb: A tuple (r, g, b) where each component is 0-255.
        """
        pass

    @property
    @abstractmethod
    def brightness(self) -> float:
        """
        The current brightness of the LED as a float between 0.0 (off) and 1.0 (full brightness).
        """
        pass

    @brightness.setter
    @abstractmethod
    def brightness(self, value: float) -> None:
        """
        Sets the brightness of the LED.
        :param value: Brightness as a float between 0.0 and 1.0.
        """
        pass

    @abstractmethod
    def is_on(self) -> bool:
        """
        Returns True if the LED is currently considered 'on' (brightness > 0).
        """
        pass

    @abstractmethod
    def off(self) -> None:
        """
        Turns the LED completely off (sets brightness to 0.0).
        """
        pass

    @abstractmethod
    def get_state(self) -> Tuple[int, int, int, float]:
        """
        Returns the full state of the LED as (r, g, b, brightness).
        """
        pass