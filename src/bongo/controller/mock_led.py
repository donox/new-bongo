# NEW FILE: src/bongo/controller/mock_led.py
class MockLED:
    def __init__(self, pin):
        self.pin = pin
        self._brightness = 0

    def on(self):
        self._brightness = 1

    def off(self):
        self._brightness = 0

    def set_brightness(self, value):
        self._brightness = value

    def get_brightness(self):
        return self._brightness

    def is_on(self):
        return self._brightness > 0
