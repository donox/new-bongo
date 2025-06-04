
from typing import List

class AnimationManager:
    def __init__(self, matrix, pixel_controller):
        self.matrix = matrix
        self.pixel_controller = pixel_controller
        self.operations = []

    def add_operation(self,  op):
        self.operations.append(op)

    def tick(self, time_now: float):
        for op in self.operations[:]:
            done = op.update(time_now)
            if done:
                self.operations.remove(op)

    def clear_operations(self):
        self.operations.clear()


