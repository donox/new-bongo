class LEDPixelOperation:
    def __init__(self, row, col, on=True):
        self.row = row
        self.col = col
        self.on = on

    def apply(self, matrix):
        brightness = 255 if self.on else 0
        matrix.set_pixel(self.row, self.col, brightness)
