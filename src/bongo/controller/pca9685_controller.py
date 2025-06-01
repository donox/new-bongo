# controller/pca9685_controller.py

from adafruit_pca9685 import PCA9685
import busio
from board import SCL, SDA
from bongo.interfaces.controller_base import BaseLEDController

class PCA9685LEDController(BaseLEDController):
    _i2c_bus = busio.I2C(SCL, SDA)
    _boards = {}

    def __init__(self, board_address: int, channel: int):
        self.channel = channel
        if board_address not in PCA9685LEDController._boards:
            pca = PCA9685(PCA9685LEDController._i2c_bus, address=board_address)
            pca.frequency = 1000
            PCA9685LEDController._boards[board_address] = pca
        self.pca = PCA9685LEDController._boards[board_address]

    def on(self):
        self.set_brightness(1.0)

    def off(self):
        self.set_brightness(0.0)

    def set_brightness(self, value: float):
        pwm = int(max(0, min(0xFFFF, value * 0xFFFF)))
        self.pca.channels[self.channel].duty_cycle = pwm
