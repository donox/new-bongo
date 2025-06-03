# NEW FILE: src/bongo/controller/mock_pca9685.py
class MockPCA9685LED:
    def __init__(self, channel, board):
        self.channel = channel
        self.board = board
        self._brightness = 0

    def on(self):
        self._brightness = 255.0

    def off(self):
        self._brightness = 0.0

    def set_brightness(self, value):
        self._brightness = value

    def get_brightness(self):
        return self._brightness

    def is_on(self):
        return self._brightness > 0
