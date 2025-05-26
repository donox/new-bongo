"""
mock_led.py
Provides a mock implementation of the IPixelController interface for testing purposes.
"""

# new-bongo/src/bongo/hardware/mock_hal.py

from bongo.interfaces.hardware import IPixelController
from typing import Tuple, List, Dict

class MockPixelController(IPixelController):
    """
    A mock implementation of the IPixelController interface for testing purposes.
    It simulates an LED matrix in memory and prints its state changes to the console.
    """
    def __init__(self, rows: int, cols: int):
        if not isinstance(rows, int) or rows <= 0:
            raise ValueError("Rows must be a positive integer.")
        if not isinstance(cols, int) or cols <= 0:
            raise ValueError("Cols must be a positive integer.")

        self._rows = rows
        self._cols = cols
        # Internal representation of the LED matrix state:
        # Dictionary with (row, col) as keys, and (r, g, b, brightness) as values
        self._pixel_state: Dict[Tuple[int, int], Tuple[int, int, int, float]] = {}
        self.initialize()
        print(f"MockPixelController: Initialized for {self._rows}x{self._cols} matrix.")

    def initialize(self) -> None:
        """
        Initializes the mock pixel controller. Clears the state.
        """
        self._pixel_state.clear()
        # Initialize all pixels to off (black, 0 brightness)
        for r in range(self._rows):
            for c in range(self._cols):
                self._pixel_state[(r, c)] = (0, 0, 0, 0.0)
        print("MockPixelController: State cleared (all pixels off).")

    def set_pixel(self, row: int, col: int, r: int, g: int, b: int, brightness: float) -> None:
        """
        Sets the color and brightness of a specific pixel in the mock matrix.
        No actual hardware interaction, just updates internal state.
        """
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            # For a mock, we might choose to raise an error or just print a warning
            # For robustness in testing, raising an error is better.
            raise ValueError(f"Pixel ({row}, {col}) is out of bounds for {self._rows}x{self._cols} matrix.")
        if not all(0 <= c <= 255 for c in [r, g, b]):
            raise ValueError("Color components (r, g, b) must be between 0 and 255.")
        if not 0.0 <= brightness <= 1.0:
            raise ValueError("Brightness value must be between 0.0 and 1.0.")

        self._pixel_state[(row, col)] = (r, g, b, brightness)
        # print(f"MockPixelController: Set pixel ({row},{col}) to Color({r},{g},{b}), Brightness={brightness:.2f}")

    def show(self) -> None:
        """
        Simulates showing the current state on the LED matrix.
        Prints a representation of the matrix to the console.
        """
        print("\n--- Mock LED Matrix State ---")
        for r in range(self._rows):
            row_str = []
            for c in range(self._cols):
                color_r, color_g, color_b, brightness = self._pixel_state[(r, c)]
                # Represent pixel state visually (e.g., 'X' for on, '.' for off)
                # Or print a simplified color/brightness if needed
                if brightness > 0.0 and (color_r, color_g, color_b) != (0, 0, 0):
                    # Basic representation: C=Cyan, M=Magenta, Y=Yellow, R=Red, G=Green, B=Blue, W=White, O=Other
                    if color_r == 255 and color_g == 255 and color_b == 255:
                        char = "W"
                    elif color_r == 255 and color_g == 0 and color_b == 0:
                        char = "R"
                    elif color_r == 0 and color_g == 255 and color_b == 0:
                        char = "G"
                    elif color_r == 0 and color_g == 0 and color_b == 255:
                        char = "B"
                    elif color_r == 255 and color_g == 255 and color_b == 0:
                        char = "Y" # Yellow
                    elif color_r == 0 and color_g == 255 and color_b == 255:
                        char = "C" # Cyan
                    elif color_r == 255 and color_g == 0 and color_b == 255:
                        char = "M" # Magenta
                    else:
                        char = "O" # Other color
                    row_str.append(f"{char}{int(brightness*9.9)}") # Show first letter of color and brightness level (0-9)
                else:
                    row_str.append("..") # Off
            print(" ".join(row_str))
        print("-----------------------------\n")

    def clear(self) -> None:
        """
        Clears all pixels in the mock matrix (sets them to black/off).
        """
        self.initialize() # Re-initialize effectively clears to off
        print("MockPixelController: All pixels cleared (set to off).")

    def shutdown(self) -> None:
        """
        Performs any necessary cleanup for the mock controller.
        """
        self._pixel_state.clear()
        print("MockPixelController: Shut down (internal state cleared).")

    def get_pixel_state(self, row: int, col: int) -> Tuple[int, int, int, float]:
        """
        Helper method for testing: returns the internal state of a specific pixel.
        """
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            raise ValueError(f"Pixel ({row}, {col}) is out of bounds for {self._rows}x{self._cols} matrix.")
        return self._pixel_state.get((row, col), (0, 0, 0, 0.0)) # Default to off if not set