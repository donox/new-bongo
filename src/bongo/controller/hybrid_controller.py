# UPDATED: controller/hybrid_controller.py

from bongo.hardware_provider import get_gpio_controller, get_pca_controller
from bongo.interfaces.controller_base import BaseLEDController

class HybridLEDController(BaseLEDController):
    def __init__(self, config: dict):
        controller_type = config['type']

        # For simplicity, each HybridLEDController manages one pixel (0,0)
        self.row = 0
        self.col = 0

        if controller_type == 'gpio':
            GPIOController = get_gpio_controller()
            self.controller = GPIOController(
                rows=1,
                cols=1,
                gpio_pins=config.get('channel', 12),  # 'channel' is the GPIO pin
            )

        elif controller_type == 'pca9685':
            PCAController = get_pca_controller()
            self.controller = PCAController(
                rows=1,
                cols=1,
                i2c_address=config.get('board', 0x40),  # default to 0x40 if not provided
                pwm_frequency=config.get('frequency', 1000),
            )

        else:
            raise ValueError(f"Unsupported controller type: {controller_type}")

    def on(self):
        self.controller.set_pixel(self.row, self.col, 255, 255, 255, 1.0)

    def off(self):
        self.controller.set_pixel(self.row, self.col, 0, 0, 0, 0.0)

    def set_brightness(self, value: float):
        self.controller.set_pixel(self.row, self.col, 255, 255, 255, value)

    def get_brightness(self):
        return self.controller.get_pixel_state(self.row, self.col)[3]
