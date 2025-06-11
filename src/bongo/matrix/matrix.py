# src/bongo/matrix/matrix.py
import logging
from typing import List, Dict, Optional, Tuple, Union

# Corrected relative imports: '..' goes up one level from the current
# 'matrix' directory to the parent 'bongo' directory, then into 'controller'.
from ..controller.hybrid_controller import HybridLEDController
from ..controller.gpio_controller import GPIOLEDController

log = logging.getLogger("bongo.matrix")

# A type hint for either controller type
AnyLEDController = Union[HybridLEDController, GPIOLEDController]


class LEDMatrix:
    """
    Represents and controls a 2D matrix of LEDs of mixed types.
    This class acts as a factory, creating the appropriate controller
    for each LED defined in the configuration.
    """

    def __init__(
            self,
            config: List[Dict],
            hardware_manager
    ):
        """
        Initializes the LEDMatrix from a configuration.

        Args:
            config: A list of dictionaries, where each defines an LED.
            hardware_manager: An initialized HardwareManager instance.
        """
        self.leds: Dict[Tuple[int, int], AnyLEDController] = {}
        self.rows: int = 0
        self.cols: int = 0
        self.hardware_manager = hardware_manager

        if not config:
            return

        max_row, max_col = -1, -1
        for entry in config:
            r, c = entry.get("row"), entry.get("col")
            led_type = entry.get("type")

            if r is None or c is None or led_type is None:
                raise ValueError(f"Config entry is missing 'row', 'col', or 'type': {entry}")

            # --- Controller Factory Logic ---
            if led_type == "pca9685":
                addr = entry.get("controller_address")
                chan = entry.get("led_channel")
                if addr is None or chan is None:
                    raise ValueError(f"PCA9685 entry is missing 'controller_address' or 'led_channel': {entry}")

                log.debug(f"Creating PCA9685 LED at ({r},{c}) on controller {hex(addr)}, channel {chan}")
                pca_controller = self.hardware_manager.get_controller(addr)
                led_controller = HybridLEDController(led_channel=chan, pca_controller=pca_controller)

            elif led_type == "gpio":
                pin = entry.get("pin")
                if pin is None:
                    raise ValueError(f"GPIO entry is missing 'pin': {entry}")

                log.debug(f"Creating GPIO LED at ({r},{c}) on pin {pin}")
                led_controller = GPIOLEDController(pin=pin)

            else:
                log.warning(f"Skipping unknown LED type '{led_type}' in config for ({r},{c})")
                continue  # Skip to the next item in the config

            self.leds[(r, c)] = led_controller
            max_row, max_col = max(max_row, r), max(max_col, c)

        self.rows = max_row + 1
        self.cols = max_col + 1

    def _normalize_brightness(self, value: float) -> float:
        """Helper to normalize brightness from 0-255 scale to 0.0-1.0 scale if needed."""
        if value > 1.0:
            norm_val = value / 255.0
            log.debug(f"Normalized brightness {value} -> {norm_val:.3f}")
            return norm_val
        log.debug(f"Brightness {value} is already normalized.")
        return value

    def get_led(self, row: int, col: int) -> Optional[AnyLEDController]:
        """Retrieves an LED controller by its row and column."""
        log.debug(f"Getting LED for coordinate ({row}, {col})")
        return self.leds.get((row, col))

    def set_pixel(self, row: int, col: int, brightness: float):
        """Sets the brightness of a single pixel in the matrix."""
        led = self.get_led(row, col)
        if led:
            normalized_brightness = self._normalize_brightness(brightness)
            log.debug(f"Passing normalized brightness {normalized_brightness:.3f} to controller at ({row},{col})")
            led.set_brightness(normalized_brightness)
        else:
            log.warning(f"Attempted to set pixel at out-of-bounds location ({row}, {col})")

    def fill(self, brightness: float):
        """Sets all LEDs in the matrix to the same brightness."""
        normalized_brightness = self._normalize_brightness(brightness)
        log.debug(f"Filling all {len(self.leds)} LEDs with normalized brightness {normalized_brightness:.3f}")
        for led in self.leds.values():
            led.set_brightness(normalized_brightness)

    def clear(self):
        """Turns all LEDs in the matrix off."""
        self.fill(0.0)

    def set_frame(self, frame: List[List[float]]):
        """
        Updates the entire matrix based on a 2D list (frame) of brightness values.

        Args:
            frame: A 2D list of brightness values (int 0-255 or float 0.0-1.0).

        Raises:
            ValueError: If the frame dimensions do not match the matrix dimensions.
        """
        frame_rows = len(frame)
        frame_cols = len(frame[0]) if frame_rows > 0 else 0

        if frame_rows != self.rows or frame_cols != self.cols:
            raise ValueError(
                f"Frame dimensions ({frame_rows}x{frame_cols}) "
                f"do not match matrix dimensions ({self.rows}x{self.cols})."
            )

        for r, row_data in enumerate(frame):
            for c, brightness in enumerate(row_data):
                self.set_pixel(r, c, brightness)

    def shutdown(self):
        """Turns all LEDs off and calls cleanup on controllers and the hardware manager."""
        log.info("Shutting down matrix...")
        self.clear()
        # Cleanup individual logical controllers
        for led in self.leds.values():
            led.cleanup()
        # Perform global cleanup (e.g., GPIO.cleanup())
        if hasattr(self.hardware_manager, 'cleanup'):
            self.hardware_manager.cleanup()

    def __iter__(self):
        return iter(self.leds.values())

    def __len__(self):
        return len(self.leds)
