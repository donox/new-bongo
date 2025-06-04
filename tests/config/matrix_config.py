
from bongo.hardware.mock_hal import MockPixelController

def simple_config():
    controller = MockPixelController(2, 2)
    return [
        {"row": r, "col": c, "type": "mock"}
        for r in range(2) for c in range(2)
    ]

def full_config():
    return [
        {"row": 0, "col": 0, "type": "mock", "pin": 1},
        {"row": 0, "col": 1, "type": "mock", "pin": 2},
        {"row": 1, "col": 0, "type": "mock", "pin": 3},
        {"row": 1, "col": 1, "type": "mock", "pin": 4},
    ]

