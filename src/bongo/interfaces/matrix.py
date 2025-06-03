# src/bongo/interfaces/matrix.py

from bongo.controller.hybrid_controller import HybridLEDController
from config.matrix_config import MATRIX_CONFIG


class LEDMatrix:
    """
    Represents a matrix of LEDs, each managed via a HybridLEDController.
    Automatically constructed from MATRIX_CONFIG.
    """

    def __init__(self, config=None):
        self.leds = []
        self.index_map = {}

        config = config or MATRIX_CONFIG
        for i, led_config in enumerate(config):
            controller = HybridLEDController(led_config)
            self.leds.append(controller)
            self.index_map[(led_config["row"], led_config["col"])] = i

    def on(self, index: int):
        self._validate_index(index)
        self.leds[index].on()

    def off(self, index: int):
        self._validate_index(index)
        self.leds[index].off()

    def set_brightness(self, index: int, value: float):
        self._validate_index(index)
        self.leds[index].set_brightness(value)

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

    def _validate_index(self, index: int):
        if not (0 <= index < len(self.leds)):
            raise IndexError(f"Invalid LED index: {index}")
