# new-bongo/src/bongo/interfaces/matrix.py

from abc import ABC, abstractmethod
from typing import Tuple, List
from bongo.interfaces.led import ILED

class ILEDMatrix(ABC):
    """
    Interface for an abstract LED matrix, providing methods to interact with
    individual LEDs within the matrix and control the overall display.
    """

    @property
    @abstractmethod
    def rows(self) -> int:
        """The number of rows in the LED matrix."""
        pass

    @property
    @abstractmethod
    def cols(self) -> int:
        """The number of columns in the LED matrix."""
        pass

    @abstractmethod
    def get_led(self, row: int, col: int) -> ILED:
        """
        Retrieves the logical LED object at the specified (row, col) coordinates.
        :param row: The row index (0-based).
        :param col: The column index (0-based).
        :return: An instance of ILED representing the LED at that position.
        :raises IndexError: If the coordinates are out of bounds.
        """
        pass

    @abstractmethod
    def get_all_leds(self) -> List[ILED]:
        """
        Returns a flat list of all ILED objects in the matrix, typically ordered
        by row, then by column.
        """
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """
        Turns off all LEDs in the matrix (sets their brightness to 0.0).
        This affects the logical state of the LEDs.
        """
        pass

    @abstractmethod
    def refresh(self) -> None:
        """
        Forces the underlying pixel controller to update the physical display
        based on the current logical states of all LEDs in the matrix.
        This method is crucial for hardware implementations that buffer changes.
        """
        pass