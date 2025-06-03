# mock_hal.py

class MockPixelController:
    def __init__(self, *args, **kwargs):
        self._pixel_state = {}  # Key: (row, col), Value: (r, g, b, brightness)

    def set_pixel(self, row: int, col: int, r: int, g: int, b: int, brightness: float):
        self._pixel_state[(row, col)] = (r, g, b, brightness)
        print(f"[MOCK] Pixel set at ({row},{col}) with RGB({r},{g},{b}) and brightness {brightness:.2f}")

    def get_pixel_state(self, row: int, col: int):
        return self._pixel_state.get((row, col), (0, 0, 0, 0.0))

    def set_brightness(self, value: float):
        self._pixel_state[(0, 0)] = (255, 255, 255, value)
        print(f"[MOCK] Fallback brightness set for (0,0) to {value:.2f}")

