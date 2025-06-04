from bongo.hardware.rpi_gpio_hal import RPiGPIOPixelController
from bongo.hardware.pca9685_hal import PCA9685PixelController
gpio_controller = RPiGPIOPixelController()
pca_controller = PCA9685PixelController(address=0x40)

MATRIX_CONFIG = [
    {"row": 0, "col": 0, "controller": gpio_controller, "pin": 12},
    {"row": 0, "col": 1, "controller": gpio_controller, "pin": 13},
    {"row": 0, "col": 2, "controller": pca_controller, "pin": 1},
    {"row": 0, "col": 3, "controller": pca_controller, "pin": 2},
    {"row": 0, "col": 4, "controller": pca_controller, "pin": 3},
    {"row": 0, "col": 5, "controller": pca_controller, "pin": 4},
]
