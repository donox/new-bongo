from bongo.hardware.rpi_gpio_hal import RPiGPIOPixelController
from bongo.hardware.pca9685_hal import PCA9685PixelController
from bongo.hardware.mock_hal import MockPixelController

class HybridLEDController:
    def __init__(self, config: dict):
        self.row = config["row"]
        self.col = config["col"]
        self.controller = self._create_controller(config)

    def _create_controller(self, config: dict):
        controller_type = config["type"]

        if controller_type == "gpio":
            return RPiGPIOPixelController(pin=config["pin"])
        elif controller_type == "pca9685":
            return RPiGPIOPixelController(address=config["address"], pin=config["pin"])
        elif controller_type == "mock":
            return MockPixelController(pin=config["pin"])
        else:
            raise ValueError(f"Unknown controller type: {controller_type}")

    def set_pixel(self, brightness: int):
        self.controller.set_brightness(brightness)

    def get_pixel(self):
        return self.controller.get_brightness()

    def on(self):
        self.set_pixel(255)

    def off(self):
        self.set_pixel(0)

    def clear(self):
        self.off()

    def get_position(self):
        return self.row, self.col
