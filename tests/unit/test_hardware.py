"""
test_hardware.py
Unit tests for the hardware abstraction layer (AbstractLED, MockLED, PCA9685LED, PiPWMLED).
"""

import unittest
import sys
from unittest.mock import MagicMock  # Keep patch here, it's good practice
from __init__ import setpath
setpath()

# Adjust the path to import from src
# This ensures that when running tests directly, Python can find the modules in 'src'
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(f"{sys.path}")
from bongo.hardware.abstract_led import AbstractLED
from bongo.hardware.mock_led import MockLED

# --- Start of Comprehensive Hardware Mocking ---
# These mocks replace the actual hardware libraries during testing
# so tests can run without physical hardware or installing all dependencies.

# Mock 'board' module (used by adafruit-circuitpython)
sys.modules['board'] = MagicMock()

# Mock 'busio' module (used by adafruit-circuitpython for I2C)
sys.modules['busio'] = MagicMock()
# Ensure busio.I2C() returns a MagicMock instance when called
sys.modules['busio'].I2C.return_value = MagicMock()
# Mock the scan method if it's ever called (though not strictly needed by current PCA9685LED code)
sys.modules['busio'].I2C.return_value.scan.return_value = [0x40] # Simulate finding a PCA9685

# Mock 'adafruit_pca9685' module
sys.modules['adafruit_pca9685'] = MagicMock()
# When PCA9685.PCA9685() is called, it should return a MagicMock instance
sys.modules['adafruit_pca9685'].PCA9685 = MagicMock()
# Configure the mock PCA9685 instance that PCA9685() will return
mock_pca_instance_return_value = MagicMock()
mock_pca_instance_return_value.frequency = 1000 # Mock frequency attribute
mock_pca_instance_return_value.channels = [MagicMock() for _ in range(16)] # Mock 16 channels
sys.modules['adafruit_pca9685'].PCA9685.return_value = mock_pca_instance_return_value


# Mock 'RPi.GPIO' module
sys.modules['RPi'] = MagicMock(__spec__=MagicMock(name='RPi', origin='mock', is_package=True))
# The __spec__ attribute with is_package=True tells Python's import system that 'RPi'
# should be treated as a package, allowing submodules like 'RPi.GPIO' to be imported.
sys.modules['RPi'].GPIO = MagicMock() # Mock the GPIO object itself
# Mock constants
sys.modules['RPi'].GPIO.BCM = 11
sys.modules['RPi'].GPIO.OUT = 1
# Mock the PWM class, ensuring it returns a MagicMock instance when called
sys.modules['RPi'].GPIO.PWM.return_value = MagicMock()
# Mock methods on the returned PWM object
sys.modules['RPi'].GPIO.PWM.return_value.start.return_value = None
sys.modules['RPi'].GPIO.PWM.return_value.ChangeDutyCycle.return_value = None
sys.modules['RPi'].GPIO.PWM.return_value.stop.return_value = None

# --- End of Comprehensive Hardware Mocking ---


# Try to import real hardware classes after mocking
# These will use the mocked modules, so they don't need actual hardware
try:
    from bongo.hardware import PCA9685LED, get_pca9685_board, _pca_boards
    PCA9685LED_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    PCA9685LED_AVAILABLE = False
    print(f"PCA9685LED not available for testing (dependencies missing/mocking issue): {e}")

try:
    from bongo.hardware.rpi_gpio_hal import PiPWMLED, cleanup_pi_pwm, _pwm_objects
    PIPWMLED_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    PIPWMLED_AVAILABLE = False
    print(f"PiPWMLED not available for testing (dependencies missing/mocking issue): {e}")


class TestAbstractLED(unittest.TestCase):
    def test_abstract_methods(self):
        # AbstractLED cannot be instantiated directly
        with self.assertRaises(TypeError):
            AbstractLED()

class TestMockLED(unittest.TestCase):
    def setUp(self):
        self.led = MockLED("test_mock")

    def test_initial_state(self):
        self.assertEqual(self.led.get_brightness(), 0)

    def test_set_brightness(self):
        self.led.set_brightness(100)
        self.assertEqual(self.led.get_brightness(), 100)
        self.led.set_brightness(255)
        self.assertEqual(self.led.get_brightness(), 255)
        self.led.set_brightness(0)
        self.assertEqual(self.led.get_brightness(), 0)

    def test_set_brightness_clamping(self):
        self.led.set_brightness(300) # Above max
        self.assertEqual(self.led.get_brightness(), 255)
        self.led.set_brightness(-50) # Below min
        self.assertEqual(self.led.get_brightness(), 0)

    def test_off(self):
        self.led.set_brightness(150)
        self.led.off()
        self.assertEqual(self.led.get_brightness(), 0)

@unittest.skipUnless(PCA9685LED_AVAILABLE, "PCA9685LED not available for testing (dependencies missing/mocking issue)")
class TestPCA9685LED(unittest.TestCase):
    def setUp(self):
        # Clear the internal cache in pca9685_hal.py to ensure a fresh mock for each test
        # This prevents tests from interfering with each other via the shared cache
        _pca_boards.clear()

        # Initialize the LED - this will internally call get_pca9685_board,
        # which will in turn use our comprehensively mocked PCA9685 class.
        self.led = PCA9685LED(0, "test_pca_led_mock") # You can choose any channel (e.g., 0) and a name
