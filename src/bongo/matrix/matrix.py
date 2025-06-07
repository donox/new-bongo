# src/bongo/matrix/matrix.py
from typing import List, Dict, Optional, Tuple

# Assuming HybridLEDController is in src.bongo.controller.hybrid_controller
from ..controller.hybrid_controller import HybridLEDController


class LEDMatrix:
    """
    Represents and controls a 2D matrix of LEDs.
    """

    def __init__(
            self,
            rows: Optional[int] = None,
            cols: Optional[int] = None,
            matrix_controller_config: Optional[Dict] = None,
            config: Optional[List[Dict]] = None,
            default_pca9685_class=None
    ):
        """
        Initializes the LEDMatrix.

        Args:
            rows: Number of rows in the matrix (if not using 'config').
            cols: Number of columns in the matrix (if not using 'config').
            matrix_controller_config: Dict with common controller details for rows/cols setup,
                                      e.g., {"controller_address": 0x40, "start_channel": 0}.
            config: A list of dictionaries, where each defines an LED, including its
                    row, col, controller_address, and led_channel.
            default_pca9685_class: The class to use for instantiating PCA9685 controllers
                                   (e.g., a mock for testing, or the actual driver class).
        """
        # Use a dictionary for direct (row, col) access instead of a list
        self.leds: Dict[Tuple[int, int], HybridLEDController] = {}
        self.rows: int = 0
        self.cols: int = 0

        if default_pca9685_class is None:
            raise ValueError("LEDMatrix constructor requires 'default_pca9685_class' to be provided.")

        if config:
            self._init_from_config(config, default_pca9685_class)
        elif rows is not None and cols is not None:
            self._init_from_rows_cols(rows, cols, matrix_controller_config, default_pca9685_class)
        else:
            # Allows creation of an empty 0x0 matrix if no config is provided
            pass

    def _init_from_config(self, config: List[Dict], default_pca9685_class):
        if not isinstance(config, list):
            raise TypeError("'config' must be a list of dictionaries.")
        if not config:
            return  # Handles empty config list, resulting in a 0x0 matrix

        max_row, max_col = -1, -1
        for entry in config:
            r, c = entry.get("row"), entry.get("col")
            if r is None or c is None:
                raise ValueError("Config items must contain 'row' and 'col' keys.")
            max_row, max_col = max(max_row, r), max(max_col, c)

            controller_address = entry.get("controller_address")
            led_channel = entry.get("led_channel")
            if controller_address is None or led_channel is None:
                raise ValueError("Config entry must contain 'controller_address' and 'led_channel'.")

            pca_class_to_use = entry.get("pca9685_class", default_pca9685_class)
            led = HybridLEDController(
                controller_address=controller_address,
                led_channel=led_channel,
                bus_number=entry.get("bus_number", 1),
                pwm_frequency=entry.get("pwm_frequency", 200),
                pca9685_class=pca_class_to_use
            )
            if (r, c) in self.leds:
                raise ValueError(f"Duplicate LED definition in config for row {r}, col {c}")
            self.leds[(r, c)] = led

        self.rows = max_row + 1
        self.cols = max_col + 1

    def _init_from_rows_cols(self, rows: int, cols: int, matrix_controller_config: Optional[Dict],
                             default_pca9685_class):
        if not (isinstance(rows, int) and rows > 0 and isinstance(cols, int) and cols > 0):
            raise ValueError("Rows and columns must be positive integers.")
        self.rows, self.cols = rows, cols

        if not matrix_controller_config or "controller_address" not in matrix_controller_config:
            raise ValueError("For rows/cols setup, 'matrix_controller_config' with 'controller_address' is required.")

        controller_address = matrix_controller_config["controller_address"]
        current_channel = matrix_controller_config.get("start_channel", 0)

        for r in range(rows):
            for c in range(cols):
                led = HybridLEDController(
                    controller_address=controller_address,
                    led_channel=current_channel,
                    bus_number=matrix_controller_config.get("bus_number", 1),
                    pwm_frequency=matrix_controller_config.get("pwm_frequency", 200),
                    pca9685_class=default_pca9685_class
                )
                self.leds[(r, c)] = led
                current_channel += 1

    def _normalize_brightness(self, value: float) -> float:
        """Helper to normalize brightness from 0-255 scale to 0.0-1.0 scale if needed."""
        if value > 1.0:
            return value / 255.0
        return value

    def get_led(self, row: int, col: int) -> Optional[HybridLEDController]:
        """Retrieves an LED controller by its row and column using dictionary lookup."""
        return self.leds.get((row, col))

    def set_pixel(self, row: int, col: int, brightness: float):
        """
        Sets the brightness of a single pixel in the matrix.

        Args:
            row: The row of the pixel.
            col: The column of the pixel.
            brightness: The brightness, can be an int (0-255) or float (0.0-1.0).
        """
        led = self.get_led(row, col)
        if led:
            normalized_brightness = self._normalize_brightness(brightness)
            led.set_brightness(normalized_brightness)
        else:
            # Optional: Log a warning for out-of-bounds access
            # logger.warning(f"Attempted to set pixel at out-of-bounds location ({row}, {col})")
            pass

    def fill(self, brightness: float):
        """
        Sets all LEDs in the matrix to the same brightness.

        Args:
            brightness: The brightness, can be an int (0-255) or float (0.0-1.0).
        """
        normalized_brightness = self._normalize_brightness(brightness)
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
        if not frame or len(frame) != self.rows or len(frame[0]) != self.cols:
            raise ValueError(
                f"Frame dimensions ({len(frame)}x{len(frame[0]) if frame else 0}) "
                f"do not match matrix dimensions ({self.rows}x{self.cols})."
            )

        for r, row_data in enumerate(frame):
            for c, brightness in enumerate(row_data):
                self.set_pixel(r, c, brightness)

    def shutdown(self):
        """Turns all LEDs off and calls cleanup on each controller."""
        self.clear()
        for led in self.leds.values():
            led.cleanup()

    def __iter__(self):
        """Allows iteration over the LED controller objects in the matrix."""
        return iter(self.leds.values())

    def __len__(self):
        """Returns the total number of LEDs in the matrix."""
        return len(self.leds)
