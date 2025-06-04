# mock_hal.py

class MockPixelController:
    def __init__(self, *args, **kwargs):
        self._pixel_state = 0

    def set_pixel(self, brightness: float):         # Deprecate
        self._pixel_state = brightness
        print(f"[MOCK] Pixel set with  brightness {brightness:.2f}")

    def get_pixel(self):         # Deprecate
        return self._pixel_state

    def get_pixel_state(self, row: int, col: int):    # Deprecate
        return self._pixel_state

    def set_brightness(self, value: float):
        self._pixel_state = value
        print(f"[MOCK] Fallback brightness set to {value:.2f}")

    def get_brightness(self):
        return self._pixel_state

