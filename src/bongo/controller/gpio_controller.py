# controller/gpio_controller.py

import RPi.GPIO as GPIO
from bongo.interfaces.controller_base import BaseLEDController

class GPIOLEDController(BaseLEDController):
    def __init__(self, pin: int):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.pin, 1000)  # 1 kHz PWM frequency
        self._pwm.start(0)

    def on(self):
        self._pwm.ChangeDutyCycle(100)

    def off(self):
        self._pwm.ChangeDutyCycle(0)

    def set_brightness(self, value: float):
        self._pwm.ChangeDutyCycle(max(0, min(100, value * 100)))
