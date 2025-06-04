from typing import List, Dict, Optional
from bongo.controller.hybrid_controller import HybridLEDController

class LEDMatrix:
    def __init__(
        self,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
        controller=None,
        config: Optional[List[Dict]] = None,
        time_now: float = 0.0,
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

    def set_pixel(self, row: int, col: int, brightness: float):
        led = self.get_led(row, col)
        led.set_pixel(brightness)

    def get_pixel(self, row: int, col: int):
        return self.get_led(row, col).get_pixel()

    def fill(self, brightness: float):
        for led in self.leds:
            led.set_pixel(brightness)

    def clear(self):
        self.fill(0.0)

    def set_frame(self, frame: List[List[float]]):
        if len(frame) != self.rows or any(len(row) != self.cols for row in frame):
            raise ValueError("Frame dimensions do not match matrix dimensions")
        for row in range(self.rows):
            for col in range(self.cols):
                self.set_pixel(row, col, frame[row][col])

    def update(self, time_now):
        self.time_now = time_now

    def shutdown(self):
        self.clear()
        for led in self.leds:
            if hasattr(led.controller, "shutdown"):
                led.controller.shutdown()
