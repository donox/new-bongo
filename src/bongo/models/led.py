# new-bongo/src/bongo/models/led.py
from bongo.interfaces.led import ILED
from typing import Tuple, Optional

class BasicLED(ILED):
    """
    A concrete implementation of the ILED interface.
    Represents the logical state of a single LED in the matrix.
    """
    def __init__(self, row: int, col: int):
        if not isinstance(row, int) or row < 0:
            raise ValueError("Row must be a non-negative integer.")
        if not isinstance(col, int) or col < 0:
            raise ValueError("Col must be a non-negative integer.")

        self._row: int = row
        self._col: int = col
        self._color: Tuple[int, int, int] = (0, 0, 0)  # Default to off (black)
        self._brightness: float = 0.0  # Default to off
        self._unique_id: str = f"R{row}C{col}"

    @property
    def row(self) -> int:
        return self._row

    @property
    def col(self) -> int:
        return self._col

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def color(self) -> Tuple[int, int, int]:
        return self._color

    @property
    def brightness(self) -> float:
        return self._brightness

    @property
    def is_on(self) -> bool:
        # An LED is considered 'on' if its brightness is > 0 and it's not pure black.
        return self._brightness > 0.0 and self._color != (0, 0, 0)

    def set_color(self, r: int, g: int, b: int) -> None:
        if not all(0 <= c <= 255 for c in [r, g, b]):
            raise ValueError("Color components (r, g, b) must be between 0 and 255.")
        self._color = (r, g, b)

    def set_brightness(self, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError("Brightness value must be between 0.0 and 1.0.")
        self._brightness = value

    def turn_on(self, color: Optional[Tuple[int, int, int]] = None, brightness: Optional[float] = None) -> None:
        if color is not None:
            self.set_color(*color)
        elif self.color == (0, 0, 0): # If previously black, set to a default (e.g., white)
            self.set_color(255, 255, 255)

        if brightness is not None:
            self.set_brightness(brightness)
        elif self.brightness == 0.0: # If previously off, set to a default brightness
            self.set_brightness(1.0) # Full brightness by default

    def turn_off(self) -> None:
        self.set_color(0, 0, 0)
        self.set_brightness(0.0)

    def toggle(self) -> None:
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on() # Will use last color/brightness or default

    def get_state(self) -> dict:
        return {
            "row": self._row,
            "col": self._col,
            "unique_id": self._unique_id,
            "color": self._color,
            "brightness": self._brightness,
            "is_on": self.is_on
        }

    def __repr__(self) -> str:
        return f"BasicLED(R{self._row}C{self._col}, Color={self._color}, Brightness={self._brightness:.2f})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BasicLED):
            return NotImplemented
        return self.row == other.row and \
               self.col == other.col and \
               self.color == other.color and \
               self.brightness == other.brightness