# new-bongo/tests/unit/test_led.py

import unittest
from bongo.models.led import BasicLED # Import the concrete LED implementation
from bongo.interfaces.led import ILED

class TestBasicLED(unittest.TestCase):
    """
    Unit tests for the BasicLED implementation.
    """

    def setUp(self):
        """Set up a fresh LED for each test."""
        self.led = BasicLED(row=0, col=0)

    def test_initialization(self):
        """Test if the LED initializes with correct defaults and properties."""
        self.assertEqual(self.led.row, 0)
        self.assertEqual(self.led.col, 0)
        self.assertEqual(self.led.unique_id, "R0C0")
        self.assertEqual(self.led.color, (0, 0, 0))
        self.assertEqual(self.led.brightness, 0.0)
        self.assertFalse(self.led.is_on)

    def test_initialization_with_different_coords(self):
        led2 = BasicLED(row=5, col=10)
        self.assertEqual(led2.row, 5)
        self.assertEqual(led2.col, 10)
        self.assertEqual(led2.unique_id, "R5C10")

    def test_set_color(self):
        """Test setting the LED color."""
        self.led.set_color(255, 0, 0) # Red
        self.assertEqual(self.led.color, (255, 0, 0))
        self.led.set_color(0, 128, 255) # Custom color
        self.assertEqual(self.led.color, (0, 128, 255))

        with self.assertRaises(ValueError):
            self.led.set_color(-1, 0, 0)
        with self.assertRaises(ValueError):
            self.led.set_color(256, 0, 0)
        with self.assertRaises(ValueError):
            self.led.set_color(0, 0, 300)

    def test_set_brightness(self):
        """Test setting the LED brightness."""
        self.led.set_brightness(0.5)
        self.assertAlmostEqual(self.led.brightness, 0.5)
        self.led.set_brightness(1.0)
        self.assertAlmostEqual(self.led.brightness, 1.0)
        self.led.set_brightness(0.0)
        self.assertAlmostEqual(self.led.brightness, 0.0)

        with self.assertRaises(ValueError):
            self.led.set_brightness(-0.1)
        with self.assertRaises(ValueError):
            self.led.set_brightness(1.1)

    def test_turn_on(self):
        """Test turning the LED on with various options."""
        self.led.turn_on()
        self.assertEqual(self.led.color, (255, 255, 255)) # Default white if initially black
        self.assertAlmostEqual(self.led.brightness, 1.0)
        self.assertTrue(self.led.is_on)

        self.led.off() # Reset
        self.led.set_color(0, 255, 0) # Set a color before turning on
        self.led.turn_on()
        self.assertEqual(self.led.color, (0, 255, 0)) # Should retain color if set
        self.assertAlmostEqual(self.led.brightness, 1.0)

        self.led.turn_on(color=(255, 0, 255), brightness=0.7)
        self.assertEqual(self.led.color, (255, 0, 255))
        self.assertAlmostEqual(self.led.brightness, 0.7)

    def test_turn_off(self):
        """Test turning the LED off."""
        self.led.set_color(255, 255, 255)
        self.led.set_brightness(1.0)
        self.assertTrue(self.led.is_on)

        self.led.off()
        self.assertEqual(self.led.color, (0, 0, 0))
        self.assertEqual(self.led.brightness, 0.0)
        self.assertFalse(self.led.is_on)

    def test_toggle(self):
        """Test toggling the LED state."""
        # Initially off
        self.assertFalse(self.led.is_on)
        self.led.toggle() # Should turn on
        self.assertTrue(self.led.is_on)
        self.assertEqual(self.led.color, (255, 255, 255)) # Default white
        self.assertAlmostEqual(self.led.brightness, 1.0)

        self.led.toggle() # Should turn off
        self.assertFalse(self.led.is_on)

        # Set a color and brightness, then toggle
        self.led.set_color(0, 0, 255)
        self.led.set_brightness(0.5)
        self.led.off() # Ensure it's off first
        self.led.toggle() # Turn on with previous color/brightness
        self.assertTrue(self.led.is_on)
        self.assertEqual(self.led.color, (0, 0, 255))
        self.assertAlmostEqual(self.led.brightness, 0.5)

    def test_is_on_property(self):
        """Test the is_on property under different conditions."""
        self.led.set_color(255, 255, 255)
        self.led.set_brightness(1.0)
        self.assertTrue(self.led.is_on)

        self.led.set_brightness(0.0) # Brightness 0
        self.assertFalse(self.led.is_on)

        self.led.set_brightness(0.5)
        self.led.set_color(0, 0, 0) # Black color
        self.assertFalse(self.led.is_on)

        self.led.set_brightness(0.0)
        self.led.set_color(0, 0, 0) # Black and 0 brightness
        self.assertFalse(self.led.is_on)

    def test_get_state(self):
        """Test the get_state method."""
        self.led.set_color(100, 150, 200)
        self.led.set_brightness(0.8)
        state = self.led.get_state()

        self.assertEqual(state["row"], 0)
        self.assertEqual(state["col"], 0)
        self.assertEqual(state["unique_id"], "R0C0")
        self.assertEqual(state["color"], (100, 150, 200))
        self.assertAlmostEqual(state["brightness"], 0.8)
        self.assertTrue(state["is_on"])

    def test_equality(self):
        led1 = BasicLED(0, 0)
        led2 = BasicLED(0, 0)
        led3 = BasicLED(0, 1)

        self.assertEqual(led1, led2)
        self.assertNotEqual(led1, led3)

        led1.set_color(255, 0, 0)
        self.assertNotEqual(led1, led2) # Color difference

        led2.set_color(255, 0, 0)
        self.assertEqual(led1, led2)

        led1.set_brightness(0.5)
        self.assertNotEqual(led1, led2) # Brightness difference

        led2.set_brightness(0.5)
        self.assertEqual(led1, led2)

        self.assertNotEqual(led1, "not an LED") # Test comparison with non-LED object


if __name__ == '__main__':
    unittest.main()