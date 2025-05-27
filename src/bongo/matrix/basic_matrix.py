from bongo.interfaces.matrix import ILEDMatrix
from bongo.interfaces.hardware import IPixelController
from bongo.interfaces.led import ILED
from bongo.models.led import BasicLED

from typing import List, Tuple, Generator, Optional


class BasicLEDMatrix(ILEDMatrix):
    """
    Concrete implementation of the ILEDMatrix interface.
    Manages a grid of BasicLED objects and coordinates updates to hardware via IPixelController.
    """

    def __init__(self):
        self._rows = 0
        self._cols = 0
        self._grid: List[List[BasicLED]] = []
        self._controller: Optional[IPixelController] = None

    def initialize(self, num_rows: int, num_cols: int, hardware_controller: IPixelController) -> None:
        self._rows = num_rows
        self._cols = num_cols
        self._controller = hardware_controller
        self._controller.initialize(num_rows, num_cols)

        self._grid = [
            [BasicLED(row=r, col=c) for c in range(num_cols)]
            for r in range(num_rows)
        ]

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    def get_led(self, row: int, col: int) -> Optional[ILED]:
        if 0 <= row < self._rows and 0 <= col < self._cols:
            return self._grid[row][col]
        return None

    def get_all_leds(self) -> Generator[ILED, None, None]:
        for row in self._grid:
            for led in row:
                yield led

    def get_row_leds(self, row: int) -> Generator[ILED, None, None]:
        if 0 <= row < self._rows:
            for led in self._grid[row]:
                yield led

    def get_col_leds(self, col: int) -> Generator[ILED, None, None]:
        if 0 <= col < self._cols:
            for r in range(self._rows):
                yield self._grid[r][col]

    def clear_all(self) -> None:
        """Turns off all LEDs logically. Call refresh() to update hardware."""
        for led in self.get_all_leds():
            led.off()

    def fill(self, r: int, g: int, b: int, brightness: float = 1.0) -> None:
        """Sets all LEDs to a uniform color and brightness."""
        for led in self.get_all_leds():
            led.set_color(r, g, b)
            led.set_brightness(brightness)

    def refresh(self) -> None:
        """Pushes the logical state to the physical hardware."""
        if not self._controller:
            raise RuntimeError("Matrix not initialized with a pixel controller.")

        for led in self.get_all_leds():
            self._controller.set_pixel(led.row, led.col, *led.color, led.brightness)
        self._controller.show()

    def set_pixel_color(self, row: int, col: int, r: int, g: int, b: int, brightness: float = 1.0) -> None:
        """Sets color and brightness for one LED and immediately updates hardware."""
        led = self.get_led(row, col)
        if led:
            led.set_color(r, g, b)
            led.set_brightness(brightness)
            self._controller.set_pixel(row, col, r, g, b, brightness)
            self._controller.show()

    def set_frame(self, frame_data: List[List[Tuple[int, int, int]]], brightness: float = 1.0) -> None:
        """Sets the entire frame at once and updates hardware."""
        if len(frame_data) != self._rows or any(len(row) != self._cols for row in frame_data):
            raise ValueError("Frame dimensions do not match matrix size.")

        for r in range(self._rows):
            for c in range(self._cols):
                self.set_pixel_color(r, c, *frame_data[r][c], brightness)

    def shutdown(self) -> None:
        """Turns off all LEDs and releases hardware."""
        self.clear_all()
        self.refresh()
        if self._controller:
            self._controller.shutdown()
