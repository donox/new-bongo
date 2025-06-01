# matrix.py

from bongo.controller.hybrid_controller import HybridLEDController
from config.matrix_config import MATRIX_CONFIG

class LEDMatrix:
    def __init__(self):
        self.leds = []
        self.index_map = {}  # Optional: map (row, col) -> index

        for i, led_config in enumerate(MATRIX_CONFIG):
            controller = HybridLEDController(led_config)
            self.leds.append(controller)
            self.index_map[(led_config['row'], led_config['col'])] = i

    def on(self, index: int):
        if 0 <= index < len(self.leds):
            self.leds[index].on()
        else:
            raise IndexError(f"Invalid LED index: {index}")

    def off(self, index: int):
        if 0 <= index < len(self.leds):
            self.leds[index].off()
        else:
            raise IndexError(f"Invalid LED index: {index}")

    def set_brightness(self, index: int, value: float):
        if 0 <= index < len(self.leds):
            self.leds[index].set_brightness(value)
        else:
            raise IndexError(f"Invalid LED index: {index}")

    def get_index(self, row: int, col: int):
        return self.index_map.get((row, col), None)

    def on_at(self, row: int, col: int):
        idx = self.get_index(row, col)
        if idx is not None:
            self.on(idx)

    def off_at(self, row: int, col: int):
        idx = self.get_index(row, col)
        if idx is not None:
            self.off(idx)

    def set_brightness_at(self, row: int, col: int, value: float):
        idx = self.get_index(row, col)
        if idx is not None:
            self.set_brightness(idx, value)
