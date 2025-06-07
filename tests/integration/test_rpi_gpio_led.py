# tests/integration/test_rpi_gpio_led.py
import pytest
import os
import time

# This check will determine if the code is running on a Raspberry Pi
IS_PI = os.path.exists('/proc/device-tree/model')

# Conditionally import RPi.GPIO only if on a Pi
if IS_PI:
    import RPi.GPIO as GPIO


# This marker will skip the entire class if not on a Raspberry Pi
@pytest.mark.skipif(not IS_PI, reason="This test requires RPi.GPIO hardware.")
class TestRpiGpioLed:
    """
    Integration tests for a single LED connected directly to Raspberry Pi GPIO pins.
    """

    @pytest.fixture
    def setup_gpio(self):
        """Fixture to set up and tear down GPIO for a test."""
        # Use a specific GPIO pin for testing
        TEST_PIN = 18  # Example: GPIO18 (Pin 12)

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
        GPIO.setwarnings(False)
        GPIO.setup(TEST_PIN, GPIO.OUT)

        # Yield the pin number to the test
        yield TEST_PIN

        # Teardown: clean up GPIO settings after the test
        print("\nCleaning up GPIO...")
        GPIO.cleanup()

    def test_led_blink(self, setup_gpio):
        """
        Tests if a single LED connected to a GPIO pin can blink.
        This is a visual confirmation test.
        """
        led_pin = setup_gpio
        print(f"\n✅ Starting test_rpi_gpio_led.py on pin {led_pin}")
        print("--> LED should turn ON for 2 seconds.")
        GPIO.output(led_pin, GPIO.HIGH)  # Turn LED ON
        time.sleep(2)

        print("--> LED should turn OFF for 2 seconds.")
        GPIO.output(led_pin, GPIO.LOW)  # Turn LED OFF
        time.sleep(2)

        print("--> LED should blink 3 times.")
        for _ in range(3):
            GPIO.output(led_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(led_pin, GPIO.LOW)
            time.sleep(0.5)

        print("✅ Test finished.")

