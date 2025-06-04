# src/bongo/controller/pca9685_controller.py

class PCA9685LEDController:
    def __init__(self, address: int, pin: int):
        from adafruit_pca9685 import PCA9685  # Lazy import
        from board import SCL, SDA
        import busio

        self.pin = pin
        i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(i2c, address=address)
        self.pca.frequency = 1000  # Typical value for LED dimming

    def on(self):
        self.pca.channels[self.pin].duty_cycle = 0xFFFF

    def off(self):
        self.pca.channels[self.pin].duty_cycle = 0x0000

    def set_color(self, color):
        # For monochrome LEDs: interpret brightness from RGB average
        brightness = int(sum(color[:3]) / 3 / 255 * 0xFFFF)
        self.pca.channels[self.pin].duty_cycle = brightness
