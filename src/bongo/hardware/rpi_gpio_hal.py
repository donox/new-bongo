import sys
from typing import List, Dict, Tuple, Any

try:
    import RPi.GPIO as GPIO
    RPi_GPIO_AVAILABLE = True
except ImportError:
    RPi_GPIO_AVAILABLE = False

from bongo.interfaces.hardware import IPixelController

_pwm_objects: Dict[int, Any] = {}


class RPiGPIOPixelController(IPixelController):
    """
    A controller for directly connected PWM-capable LEDs on Raspberry Pi GPIO pins.
    Assumes single-color LEDs. RGB is ignored; only brightness is used.
    """

    def __init__(self, rows: int, cols: int, gpio_pins: List[int], frequency: int = 1000):
        if not RPi_GPIO_AVAILABLE:
            raise RuntimeError("RPi.GPIO library not available. Cannot initialize RPiGPIOPixelController.")

        if not isinstance(rows, int) or rows <= 0:
            raise ValueError("Rows must be a positive integer.")
        if not isinstance(cols, int) or cols <= 0:
            raise ValueError("Cols must be a positive integer.")
        if not isinstance(gpio_pins, list) or not all(isinstance(p, int) for p in gpio_pins):
            raise TypeError("gpio_pins must be a list of integers.")

        total_pixels = rows * cols
        if len(gpio_pins) != total_pixels:
            raise ValueError(
                f"Number of provided GPIO pins ({len(gpio_pins)}) "
                f"does not match the total pixels in the matrix ({total_pixels})."
            )

        self._rows = rows
        self._cols = cols
        self._gpio_pins = gpio_pins
        self._frequency = frequency

        # Map (row, col) to GPIO pin
        self._pixel_to_gpio_map: Dict[Tuple[int, int], int] = {}
        for r in range(self._rows):
            for c in range(self._cols):
                linear_index = r * self._cols + c
                self._pixel_to_gpio_map[(r, c)] = self._gpio_pins[linear_index]

        self._pixel_state: Dict[Tuple[int, int], Tuple[int, int, int, float]] = {}
        self.initialize()

        print(f"RPiGPIOPixelController: Initialized for {rows}x{cols} matrix on GPIO pins {gpio_pins}.")

    def initialize(self, num_rows: int = None, num_cols: int = None) -> None:
        GPIO.setmode(GPIO.BCM)
        for pin in self._gpio_pins:
            GPIO.setup(pin, GPIO.OUT)
            print(f"RPiGPIOPixelController: Setting pin {pin} to {pin}", flush=True)

            # If a PWM object already exists for this pin, stop and delete it
            if pin in _pwm_objects:
                try:
                    _pwm_objects[pin].stop()
                except Exception as e:
                    print(f"Warning: Error stopping PWM for pin {pin}: {e}")
                del _pwm_objects[pin]

            pwm = GPIO.PWM(pin, self._frequency)
            pwm.start(0)  # Start with 0% duty cycle (off)
            _pwm_objects[pin] = pwm

        print(f"RPiGPIOPixelController: PWM initialized for pins {self._gpio_pins}")

    def set_pixel(self, row: int, col: int, r: int, g: int, b: int, brightness: float) -> None:
        if not RPi_GPIO_AVAILABLE:
            print("RPi.GPIO not available, skipping set_pixel.")
            return

        if not (0 <= row < self._rows and 0 <= col < self._cols):
            raise ValueError(f"Pixel ({row}, {col}) is out of bounds for {self._rows}x{self._cols} matrix.")
        if not all(0 <= c <= 255 for c in [r, g, b]):
            raise ValueError("Color components (r, g, b) must be between 0 and 255.")
        if not 0.0 <= brightness <= 1.0:
            raise ValueError("Brightness value must be between 0.0 and 1.0.")

        self._pixel_state[(row, col)] = (r, g, b, brightness)
        gpio_pin = self._pixel_to_gpio_map[(row, col)]

        if gpio_pin not in _pwm_objects:
            raise RuntimeError(f"PWM object for GPIO pin {gpio_pin} not initialized.")

        duty_cycle = brightness * 100
        _pwm_objects[gpio_pin].ChangeDutyCycle(duty_cycle)

    def clear(self) -> None:
        for pin in self._gpio_pins:
            if pin in _pwm_objects:
                _pwm_objects[pin].ChangeDutyCycle(0)
        self._pixel_state.clear()
        print("RPiGPIOPixelController: All pixels cleared (set to off).")

    def show(self) -> None:
        for (row, col), (r, g, b, brightness) in self._pixel_state.items():
            self.set_pixel(row, col, r, g, b, brightness)

    def shutdown(self) -> None:
        print("RPiGPIOPixelController: Shutting down and cleaning up GPIO resources.")
        for pwm in _pwm_objects.values():
            pwm.stop()
        _pwm_objects.clear()
        GPIO.cleanup()
        self.clear()
        print("RPi.GPIO cleanup completed.")

    def get_pixel_state(self, row: int, col: int) -> Tuple[int, int, int, float]:
        """
        Return the current (r, g, b, brightness) for the pixel at (row, col).
        """
        return self._pixel_state.get((row, col), (0, 0, 0, 0.0))

def clear_pwm_objects():
    global _pwm_objects
    for pwm in _pwm_objects.values():
        pwm.stop()
    _pwm_objects.clear()
