from bongo.interfaces.hardware import IPixelController
from typing import Tuple, Dict


class MockPixelController(IPixelController):
    """
    A mock implementation of IPixelController for testing purposes.
    Simulates an LED matrix and tracks internal pixel states.
    """

    def __init__(self, rows: int, cols: int):
        if rows <= 0 or cols <= 0:
            raise ValueError("Matrix dimensions must be positive integers.")
        self._rows = rows
        self._cols = cols
        self._pixel_state: Dict[Tuple[int, int], Tuple[int, int, int, float]] = {}
        self.initialize(rows, cols)

    def initialize(self, num_rows: int = None, num_cols: int = None, **kwargs) -> None:
        """Initializes internal state with all pixels off."""
        if num_rows is not None:
            self._rows = num_rows
        if num_cols is not None:
            self._cols = num_cols

        self._pixel_state = {
            (r, c): (0, 0, 0, 0.0)
            for r in range(self._rows)
            for c in range(self._cols)
        }

    def set_pixel(self, row: int, col: int, r: int, g: int, b: int, brightness: float = 1.0) -> None:
        """Sets the simulated color and brightness of a pixel."""
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            raise ValueError(f"Pixel ({row}, {col}) is out of bounds.")

        if not all(0 <= val <= 255 for val in (r, g, b)):
            raise ValueError("Color values must be between 0 and 255.")

        if not 0.0 <= brightness <= 1.0:
            raise ValueError("Brightness must be between 0.0 and 1.0.")

        self._pixel_state[(row, col)] = (r, g, b, brightness)

    def show(self) -> None:
        """Simulates displaying the current matrix state."""
        print("\nMock LED Matrix State:")
        for r in range(self._rows):
            row_repr = ""
            for c in range(self._cols):
                r_val, g_val, b_val, bright = self._pixel_state.get((r, c), (0, 0, 0, 0.0))
                if bright > 0 and (r_val, g_val, b_val) != (0, 0, 0):
                    row_repr += "█"
                else:
                    row_repr += "·"
            print(row_repr)
        print()

    def clear(self) -> None:
        """Turns off all simulated pixels."""
        for key in self._pixel_state:
            self._pixel_state[key] = (0, 0, 0, 0.0)

    def shutdown(self) -> None:
        """Simulates shutting down hardware and clearing state."""
        self._pixel_state.clear()

    def get_pixel_state(self, row: int, col: int) -> Tuple[int, int, int, float]:
        """Returns the current simulated state of a pixel (for testing)."""
        if (row, col) not in self._pixel_state:
            raise ValueError(f"Pixel ({row}, {col}) is not defined.")
        return self._pixel_state[(row, col)]
