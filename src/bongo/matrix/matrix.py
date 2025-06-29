# src/bongo/matrix/matrix.py
import logging
from typing import List, Dict, Optional, Tuple, Union

# Corrected relative imports
from ..controller.hybrid_controller import HybridLEDController
from ..controller.gpio_controller import GPIOLEDController

log = logging.getLogger("bongo.matrix")

AnyLEDController = Union[HybridLEDController, GPIOLEDController]


class LEDMatrix:
    """
    Represents and controls a 2D matrix of LEDs of mixed types.
    This class acts as a factory, creating the appropriate controller
    for each LED defined in the configuration.
    """

    def __init__(self, config: List[Dict], hardware_manager):
        self.leds: Dict[Tuple[int, int], AnyLEDController] = {}
        self.rows: int = 0
        self.cols: int = 0
        self.hardware_manager = hardware_manager

        if not config:
            return

        max_row, max_col = -1, -1
        for entry in config:
            r, c, led_type = entry.get("row"), entry.get("col"), entry.get("type")
            if r is None or c is None or led_type is None:
                raise ValueError(f"Config entry is missing 'row', 'col', or 'type': {entry}")

            if led_type == "pca9685":
                addr, chan = entry.get("controller_address"), entry.get("led_channel")
                if addr is None or chan is None:
                    raise ValueError(f"PCA9685 entry is missing 'controller_address' or 'led_channel': {entry}")
                pca_controller = self.hardware_manager.get_controller(addr)
                led_controller = HybridLEDController(led_channel=chan, pca_controller=pca_controller)
            elif led_type == "gpio":
                pin = entry.get("pin")
                if pin is None:
                    raise ValueError(f"GPIO entry is missing 'pin': {entry}")
                led_controller = GPIOLEDController(pin=pin)
            else:
                log.warning(f"Skipping unknown LED type '{led_type}' for ({r},{c})")
                continue

            self.leds[(r, c)] = led_controller
            max_row, max_col = max(max_row, r), max(max_col, c)

        self.rows = max_row + 1
        self.cols = max_col + 1

    def _normalize_brightness(self, value: float) -> float:
        return value / 255.0 if value > 1.0 else value

    def get_led(self, row: int, col: int) -> Optional[AnyLEDController]:
        # print(f"Looking for key: ({row}, {col})")
        # print(f"Available keys: {list(self.leds.keys())}")
        result =  self.leds.get((row, col))
        return result

    def set_pixel(self, row: int, col: int, brightness: float):
        led = self.get_led(row, col)
        if led:
            brt = self._normalize_brightness(brightness)
            led.set_brightness(brt)

    def fill(self, brightness: float):
        normalized_brightness = self._normalize_brightness(brightness)
        for led in self.leds.values():
            led.set_brightness(normalized_brightness)

    def clear(self):
        self.fill(0.0)

    def set_frame(self, frame: List[List[float]]):
        """
        Updates the entire matrix based on a 2D list (frame) of brightness values.
        """
        frame_rows = len(frame)
        frame_cols = len(frame[0]) if frame_rows > 0 else 0
        if frame_rows != self.rows or frame_cols != self.cols:
            raise ValueError(
                f"Frame dimensions ({frame_rows}x{frame_cols}) do not match matrix dimensions ({self.rows}x{self.cols}).")

        for r, row_data in enumerate(frame):
            for c, brightness in enumerate(row_data):
                self.set_pixel(r, c, brightness)

    def shutdown(self):
        """Turns all LEDs off and calls cleanup on controllers and the hardware manager."""
        self.clear()
        for led in self.leds.values():
            led.cleanup()
        if hasattr(self.hardware_manager, 'cleanup'):
            self.hardware_manager.cleanup()

    def __iter__(self):
        return iter(self.leds.values())

    def __len__(self):
        return len(self.leds)
