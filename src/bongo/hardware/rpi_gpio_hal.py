# new-bongo/src/bongo/hardware/rpi_gpio_hal.py

from bongo.interfaces.hardware import IPixelController
from typing import Dict, Tuple, List, Optional

try:
    import RPi.GPIO as GPIO
    RPi_GPIO_AVAILABLE = True
except ImportError:
    RPi_GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not found. RPiGPIOPixelController will not function.")

# Keep track of initialized PWM objects to avoid re-initializing
_pwm_objects: Dict[int, GPIO.PWM] = {}


class RPiGPIOPixelController(IPixelController):
    """
    A concrete implementation of the IPixelController interface for controlling
    LEDs directly via Raspberry Pi GPIO hardware PWM pins.

    Assumes single-color LEDs are connected to specific GPIO pins.
    You must provide a list of GPIO pins corresponding to your matrix layout.
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
        print(f"RPiGPIOPixelController: Initialized for {self._rows}x{self._cols} matrix on GPIO pins {gpio_pins}.")

    def initialize(self) -> None:
        """
        Initializes RPi.GPIO settings and sets up PWM for each specified pin.
        """
        if not RPi_GPIO_AVAILABLE:
            raise RuntimeError("RPi.GPIO library not available. Initialization failed.")

        GPIO.setmode(GPIO.BCM)  # Use BCM numbering for GPIO pins
        GPIO.setwarnings(False) # Disable warnings about channels already in use, etc. (for robustness)

        for pin in self._gpio_pins:
            if pin not in _pwm_objects:
                GPIO.setup(pin, GPIO.OUT)
                pwm = GPIO.PWM(pin, self._frequency)
                pwm.start(0)  # Start with 0% duty cycle (off)
                _pwm_objects[pin] = pwm
                # print(f"RPiGPIOPixelController: GPIO {pin} initialized at {self._frequency} Hz.") # Debug
            else:
                # If already initialized, ensure its frequency is correct
                # (RPi.GPIO doesn't have a direct ChangeFrequency for PWM objects)
                # For simplicity, we assume it's correctly set or re-create if truly needed.
                # print(f"RPiGPIOPixelController: Using existing PWM on GPIO {pin}.") # Debug
                pass

        # Clear all pixels to off state internally and on the board
        self.clear()

    def set_pixel(self, row: int, col: int, r: int, g: int, b: int, brightness: float) -> None:
        """
        Sets the brightness of a specific pixel using RPi.GPIO PWM.
        The RGB components are currently ignored, as this assumes single-color LEDs.
        Brightness (0.0-1.0) is mapped to 0-100% duty cycle.
        """
        if not RPi_GPIO_AVAILABLE:
            print("RPi.GPIO not available, skipping set_pixel.")
            return

        if not (0 <= row < self._rows and 0 <= col < self._cols):
            raise ValueError(f"Pixel ({row}, {col}) is out of bounds for {self._rows}x{self._cols} matrix.")
        if not all(0 <= c <= 255 for c in [r, g, b]):
            raise ValueError("Color components (r, g, b) must be between 0 and 255.")
        if not 0.0 <= brightness <= 1.0:
            raise ValueError("Brightness value must be between 0.0 and 1.0.")

        # Store the logical state
        self._pixel_state[(row, col)] = (r, g, b, brightness)

        gpio_pin = self._pixel_to_gpio_map[(row, col)]
        if gpio_pin not in _pwm_objects:
            raise RuntimeError(f"PWM object for GPIO pin {gpio_pin} not initialized.")

        # Convert 0.0-1.0 brightness to 0-100% duty cycle
        duty_cycle = brightness * 100.0

        _pwm_objects[gpio_pin].ChangeDutyCycle(duty_cycle)
        # print(f"RPiGPIO: Set ({row},{col}) pin {gpio_pin} to {duty_cycle:.2f}% (brightness {brightness:.2f})") # Debug

    def show(self) -> None:
        """
        For RPi.GPIO, changing the duty cycle directly updates the output.
        This method serves as a placeholder for consistency with other controllers
        that might require a separate 'show' or 'flush' command.
        """
        # No explicit action needed for RPi.GPIO after set_pixel
        pass

    def clear(self) -> None:
        """
        Turns off all pixels in the matrix by setting their PWM duty cycle to 0%.
        """
        if not RPi_GPIO_AVAILABLE:
            print("RPi.GPIO not available, skipping clear.")
            return

        for pin in self._gpio_pins:
            if pin in _pwm_objects:
                _pwm_objects[pin].ChangeDutyCycle(0)  # Turn off

        # Also clear internal state
        for r in range(self._rows):
            for c in range(self._cols):
                self._pixel_state[(r, c)] = (0, 0, 0, 0.0)
        print("RPiGPIOPixelController: All pixels cleared (set to off).")

    def shutdown(self) -> None:
        """
        Shuts down the RPi.GPIO controller, turning off all LEDs and releasing GPIO resources.
        """
        if not RPi_GPIO_AVAILABLE:
            print("RPi.GPIO not available, skipping shutdown.")
            return

        print("RPiGPIOPixelController: Shutting down and cleaning up GPIO resources.")
        self.clear() # Ensure all LEDs are off

        for pin in list(_pwm_objects.keys()): # Iterate over a copy to allow modification
            pwm_obj = _pwm_objects.pop(pin)
            pwm_obj.stop() # Stop the PWM signal
            # GPIO.cleanup() will handle cleaning up GPIO.OUT settings

        # Only call GPIO.cleanup() if no other PWM objects are active to avoid disrupting them
        if not _pwm_objects: # If this is the last controller using _pwm_objects
            try:
                GPIO.cleanup()
                print("RPi.GPIO cleanup completed.")
            except Exception as e:
                print(f"Error during RPi.GPIO cleanup: {e}")