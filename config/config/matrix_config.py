
from bongo.hardware.mock_hal import MockPixelController

def simple_config():
    controller = MockPixelController(2, 2)
    return [
        {"row": r, "col": c, "controller": controller}
        for r in range(2) for c in range(2)
    ]

def full_config():
    controller1 = MockPixelController(3, 3)
    controller2 = MockPixelController(3, 3)
    return [
        {"row": 0, "col": 0, "controller": controller1},
        {"row": 0, "col": 1, "controller": controller2},
        {"row": 1, "col": 0, "controller": controller1},
        {"row": 1, "col": 1, "controller": controller2}
    ]
