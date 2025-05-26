# new-bongo/src/bongo/hardware/pca9685_hal.py

import board
import busio
from adafruit_pca9685 import PCA9685
from bongo.interfaces.hardware import IPixelController
from typing import Dict, Tuple, List, Optional

# Dictionary to hold PCA9685 instances by their I2C address
# This ensures that only one instance of a PCA9685 board is created per address.
_pca_boards: Dict[int, PCA9685] = {}


class PCA9685PixelController(IPixelController):
    """
    A concrete implementation of the IPixelController interface for controlling
    LEDs via a PCA9685 PWM driver board.

    Assumes single-color LEDs are connected to individual PCA9685 channels.
    For RGB LEDs, a more complex channel mapping (3 channels per pixel) would be needed.
    """

    # Default I2C address for PCA9685
    DEFAULT_I2C_ADDRESS = 0x40

    def __init__(self, rows: int, cols: int, i2c_address: int = DEFAULT_I2C_ADDRESS, pwm_frequency: int = 1000):
        if not isinstance(rows, int) or rows <= 0:
            raise ValueError("Rows must be a positive integer.")
        if not isinstance(cols, int) or cols <= 0:
            raise ValueError("Cols must be a positive integer.")

        self._rows = rows
        self._cols = cols
        self._i2c_address = i2c_address
        self._pwm_frequency = pwm_frequency

        # Validate that the matrix size fits within a single PCA9685's channels (16 channels)
        if self._rows * self._cols > 16:
            raise ValueError(
                f"Matrix size ({self._rows}x{self._cols} = {self._rows * self._cols} LEDs) "
                "exceeds the 16 channels of a single PCA9685 board. "
                "This controller currently supports only a single PCA9685."
            )

        self._pca: Optional[PCA9685] = None
        self._pixel_state: Dict[Tuple[int, int], Tuple[int, int, int, float]] = {}

        # Pre-calculate pixel-to-channel mapping for efficiency
        # Assumes a simple linear mapping: (row, col) -> channel_index
        self._pixel_to_channel_map: Dict[Tuple[int, int], int] = {}
        for r in range(self._rows):
            for c in range(self._cols):
                self._pixel_to_channel_map[(r, c)] = r * self._cols + c

        self.initialize()
        print(
            f"PCA9685PixelController: Initialized for {self._rows}x{self._cols} matrix at address 0x{self._i2c_address:X}.")

    def initialize(self) -> None:
        """
        Initializes the PCA9685 board. This method handles I2C bus setup
        and ensures the PCA9685 instance is ready.
        """
        if self._pca is None:
            if self._i2c_address not in _pca_boards:
                try:
                    i2c = busio.I2C(board.SCL, board.SDA)
                    pca = PCA9685(i2c, address=self._i2c_address)
                    pca.frequency = self._pwm_frequency
                    _pca_boards[self._i2c_address] = pca
                    print(
                        f"PCA9685 board at address 0x{self._i2c_address:X} initialized with frequency {pca.frequency} Hz.")
                except (ValueError, RuntimeError) as e:
                    raise RuntimeError(
                        f"Could not initialize PCA9685 at address 0x{self._i2c_address:X}. "
                        "Check wiring and I2C connection."
                    ) from e
            self._pca = _pca_boards[self._i2c_address]

        # Clear all pixels to off state internally and on the board
        self.clear()

    def set_pixel(self, row: int, col: int, r: int, g: int, b: int, brightness: float) -> None:
        """
        Sets the color and brightness of a specific pixel on the PCA9685.
        The RGB components are currently ignored, as this assumes single-color LEDs.
        Brightness (0.0-1.0) is mapped to PCA9685's 16-bit PWM duty cycle.
        """
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            raise ValueError(f"Pixel ({row}, {col}) is out of bounds for {self._rows}x{self._cols} matrix.")
        if not all(0 <= c <= 255 for c in [r, g, b]):
            raise ValueError("Color components (r, g, b) must be between 0 and 255.")
        if not 0.0 <= brightness <= 1.0:
            raise ValueError("Brightness value must be between 0.0 and 1.0.")

        if self._pca is None:
            raise RuntimeError("PCA9685PixelController not initialized. Call initialize() first.")

        # Store the logical state for potential future use or debugging
        self._pixel_state[(row, col)] = (r, g, b, brightness)

        channel_index = self._pixel_to_channel_map[(row, col)]

        # Convert 0.0-1.0 brightness to 0-65535 (16-bit) PWM value
        # We effectively treat brightness as a master intensity for the single-color LED
        pwm_value = int(brightness * 0xFFFF)  # 0xFFFF is 65535

        # Set the PWM duty cycle for the specific channel
        self._pca.channels[channel_index].duty_cycle = pwm_value
        # print(f"PCA9685: Set ({row},{col}) channel {channel_index} to PWM {pwm_value} (brightness {brightness:.2f})") # Debug

    def show(self) -> None:
        """
        For PCA9685, setting the duty cycle directly updates the output.
        This method serves as a placeholder for consistency with other controllers
        that might require a separate 'show' or 'flush' command.
        """
        # No explicit action needed for PCA9685 after set_pixel
        pass

    def clear(self) -> None:
        """
        Turns off all pixels in the matrix by setting their PWM duty cycle to 0.
        """
        if self._pca is None:
            raise RuntimeError("PCA9685PixelController not initialized. Call initialize() first.")

        for channel_index in self._pixel_to_channel_map.values():
            self._pca.channels[channel_index].duty_cycle = 0  # Turn off

        # Also clear internal state
        for r in range(self._rows):
            for c in range(self._cols):
                self._pixel_state[(r, c)] = (0, 0, 0, 0.0)
        print("PCA9685PixelController: All pixels cleared (set to off).")

    def shutdown(self) -> None:
        """
        Shuts down the PCA9685 controller, turning off all LEDs and releasing resources.
        """
        if self._pca is not None:
            self.clear()  # Ensure all LEDs are off
            # Optionally, you might want to remove the PCA from the global _pca_boards cache
            # if it's the only reference and you want to allow re-initialization cleanly.
            if self._i2c_address in _pca_boards:
                del _pca_boards[self._i2c_address]
            self._pca = None
            print(f"PCA9685PixelController: Shut down (PCA9685 at 0x{self._i2c_address:X} released).")