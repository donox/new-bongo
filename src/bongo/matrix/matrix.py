from typing import List, Dict, Tuple, Optional
from bongo.controller.hybrid_controller import HybridLEDController


class LEDMatrix:
    def __init__(
        self,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
        controller=None,
        config: Optional[List[Dict]] = None,
    ):
        self.leds: List[HybridLEDController] = []

        if config:
            self.rows = max(item["row"] for item in config) + 1
            self.cols = max(item["col"] for item in config) + 1
            for entry in config:
                led = HybridLEDController(entry)
                self.leds.append(led)
        elif rows is not None and cols is not None and controller is not None:
            self.rows = rows
            self.cols = cols
            self.controller = controller
            for row in range(rows):
                for col in range(cols):
                    led = HybridLEDController({"row": row, "col": col, "controller": controller})
                    self.leds.append(led)
        else:
            raise ValueError("Provide either (rows, cols, controller) or a config list")

    def get_led(self, row: int, col: int):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError("LED coordinates out of range")
        return self.leds[row * self.cols + col]

    def set_pixel(self, row: int, col: int, r: int, g: int, b: int, brightness: float):
        led = self.get_led(row, col)
        led.set_pixel(r, g, b, brightness)

    def fill(self, r: int, g: int, b: int, brightness: float):
        for led in self.leds:
            led.set_pixel(r, g, b, brightness)

    def clear(self):
        self.fill(0, 0, 0, 0.0)

    def set_frame(self, frame: List[List[tuple]]):
        if len(frame) != self.rows or any(len(row) != self.cols for row in frame):
            raise ValueError("Frame dimensions do not match matrix dimensions")

        for row in range(self.rows):
            for col in range(self.cols):
                r, g, b, brightness = frame[row][col]
                self.set_pixel(row, col, r, g, b, brightness)

    def shutdown(self):
        self.clear()
        if hasattr(self.controller, "shutdown"):
            self.controller.shutdown()