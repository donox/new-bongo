# controller/hybrid_controller.py

from bongo.controller.gpio_controller import GPIOLEDController
from bongo.controller.pca9685_controller import PCA9685LEDController
from bongo.interfaces.controller_base import BaseLEDController

class HybridLEDController(BaseLEDController):
    def __init__(self, config: dict):
        controller_type = config['type']
        if controller_type == 'gpio':
            self.controller = GPIOLEDController(pin=config['channel'])  # channel = pin
        elif controller_type == 'pca9685':
            self.controller = PCA9685LEDController(
                board_address=config['board'],
                channel=config['channel']
            )
        else:
            raise ValueError(f"Unsupported controller type: {controller_type}")

    def on(self):
        self.controller.on()

    def off(self):
        self.controller.off()

    def set_brightness(self, value: float):
        self.controller.set_brightness(value)
