
from typing import List
from bongo.operations.led_operation import LEDOperation

class AnimationManager:
    def __init__(self, matrix, pixel_controller):
        self.matrix = matrix
        self.pixel_controller = pixel_controller
        self.operations = []

    def add_operation(self, led, op):
        op.controller = led.controller
        self.operations.append(op)

    def tick(self, time_now: float):
        for op in self.operations[:]:
            done = op.update(time_now)
            if done:
                self.operations.remove(op)

