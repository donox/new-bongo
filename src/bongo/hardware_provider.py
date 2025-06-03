# src/bongo/hardware_provider.py

import os

USE_REAL = os.getenv("USE_REAL_HARDWARE") == "1"

if USE_REAL:
    from bongo.hardware.rpi_gpio_hal import RPiGPIOPixelController as GPIOController
    from bongo.hardware.pca9685_hal import PCA9685PixelController as PCAController
else:
    from bongo.hardware.mock_hal import MockPixelController as GPIOController
    from bongo.hardware.mock_hal import MockPixelController as PCAController  # Reuse the mock for both

def get_gpio_controller():
    return GPIOController

def get_pca_controller():
    return PCAController
