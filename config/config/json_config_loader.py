
import json
from bongo.hardware.mock_hal import MockPixelController

def load_matrix_config(path: str):
    with open(path, 'r') as f:
        data = json.load(f)

    config = []
    for entry in data:
        controller_type = entry.get("type")
        if controller_type == "mock":
            controller = MockPixelController(1, 1)
        else:
            raise ValueError(f"Unknown controller type: {controller_type}")

        config.append({
            "row": entry["row"],
            "col": entry["col"],
            "controller": controller
        })
    return config
