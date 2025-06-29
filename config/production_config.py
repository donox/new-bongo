from bongo.hardware.rpi_gpio_hal import RPiGPIOPixelController
from bongo.hardware.pca9685_hal import PCA9685PixelController

gpio_controller = RPiGPIOPixelController()
pca_controller = PCA9685PixelController(address=0x40)

MATRIX_CONFIG = [
    {"row": 0, "col": 0, "controller": gpio_controller, "pin": 12},
    {"row": 0, "col": 1, "controller": gpio_controller, "pin": 13},
    {"row": 0, "col": 2, "controller": pca_controller, "pin": 0},  # pins number 0-15
    {"row": 0, "col": 3, "controller": pca_controller, "pin": 1},
    {"row": 0, "col": 4, "controller": pca_controller, "pin": 2},
    {"row": 0, "col": 5, "controller": pca_controller, "pin": 3},
    {"row": 1, "col": 0, "controller": pca_controller, "pin": 4},
    {"row": 1, "col": 1, "controller": pca_controller, "pin": 5},
    {"row": 1, "col": 2, "controller": pca_controller, "pin": 6},
    {"row": 1, "col": 3, "controller": pca_controller, "pin": 7},
    {"row": 1, "col": 4, "controller": pca_controller, "pin": 8},
    {"row": 1, "col": 5, "controller": pca_controller, "pin": 9},
    {"row": 2, "col": 0, "controller": pca_controller, "pin": 10},
    {"row": 2, "col": 1, "controller": pca_controller, "pin": 11},
    {"row": 2, "col": 2, "controller": pca_controller, "pin": 12},
    {"row": 2, "col": 3, "controller": pca_controller, "pin": 13},
    {"row": 2, "col": 4, "controller": pca_controller, "pin": 14},
    {"row": 2, "col": 5, "controller": pca_controller, "pin": 15},
]
#
