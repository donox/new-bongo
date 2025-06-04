# src/bongo/controller/gpio_controller.py

class GPIOLEDController:
    def __init__(self, pin: int):
        import RPi.GPIO as GPIO  # Lazy import inside the constructor
        self.GPIO = GPIO
        self.pin = pin
        self.GPIO.setmode(GPIO.BOARD)
        self.GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        self.GPIO.output(self.pin, self.GPIO.HIGH)

    def off(self):
        self.GPIO.output(self.pin, self.GPIO.LOW)

    def set_color(self, color):
        # GPIO LEDs are assumed single-color (on/off); ignore color
        self.on()
