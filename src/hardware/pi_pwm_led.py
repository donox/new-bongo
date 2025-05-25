"""
pi_pwm_led.py
Implements the AbstractLED for individual LEDs connected directly to Raspberry Pi
hardware PWM pins.

Note: Hardware PWM is available only on specific GPIO pins (e.g., GPIO12, 13, 18, 19).
Ensure your chosen pin supports hardware PWM.
This implementation uses RPi.GPIO.
"""

import RPi.GPIO as GPIO
from src.hardware.abstract_led import AbstractLED

# Keep track of initialized PWM objects to avoid re-initializing
_pwm_objects = {}

class PiPWMLED(AbstractLED):
    """
    An LED controlled by a specific hardware PWM pin on the Raspberry Pi.
    """
    def __init__(self, led_id: str, gpio_pin: int, frequency: int = 1000):
        self.led_id = led_id
        self._gpio_pin = gpio_pin
        self._frequency = frequency
        self._current_brightness = 0

        # Check if the pin is already initialized for PWM
        if gpio_pin not in _pwm_objects:
            GPIO.setmode(GPIO.BCM) # Use BCM numbering
            GPIO.setup(self._gpio_pin, GPIO.OUT)
            self._pwm = GPIO.PWM(self._gpio_pin, self._frequency)
            self._pwm.start(0) # Start with 0% duty cycle (off)
            _pwm_objects[gpio_pin] = self._pwm
            print(f"PiPWMLED {self.led_id}: Initialized on GPIO {self._gpio_pin} at {self._frequency} Hz.")
        else:
            self._pwm = _pwm_objects[gpio_pin]
            print(f"PiPWMLED {self.led_id}: Using existing PWM on GPIO {self._gpio_pin}.")

        self.off() # Ensure LED is off on initialization

    def set_brightness(self, brightness: int):
        """
        Sets the brightness of the LED using PWM duty cycle.
        Brightness is an integer between 0 (off) and 255 (full brightness).
        """
        # Ensure brightness is within expected range (0-255)
        brightness = max(0, min(255, brightness))
        self._current_brightness = brightness

        # Convert 0-255 brightness to 0-100% duty cycle for RPi.GPIO PWM
        duty_cycle = (brightness / 255.0) * 100

        # print(f"PiPWMLED {self.led_id}: Setting duty cycle to {duty_cycle:.2f}% (brightness {brightness}).") # Debug
        self._pwm.ChangeDutyCycle(duty_cycle)

    def get_brightness(self) -> int:
        """
        Returns the current logical brightness of the LED (0-255).
        """
        return self._current_brightness

    def off(self):
        """
        Turns the LED completely off.
        """
        self.set_brightness(0)

# Important: You might want a cleanup function for RPi.GPIO at program exit
def cleanup_pi_pwm():
    """
    Cleans up all initialized RPi.GPIO PWM pins.
    Call this before your program exits.
    """
    print("Cleaning up RPi.GPIO PWM pins...")
    for pwm_obj in _pwm_objects.values():
        pwm_obj.stop()
    GPIO.cleanup()
    _pwm_objects.clear()
    print("RPi.GPIO cleanup complete.")