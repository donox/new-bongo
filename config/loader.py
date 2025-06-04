import json
from typing import List, Dict, Any
from pathlib import Path
from bongo.hardware.pca9685_hal import PCA9685Controller
from bongo.hardware.rpi_gpio_hal import GPIOController

# Cache of controller instances to reuse the same address/controller if specified multiple times
_controller_cache = {}

def get_controller(controller_type: str, **kwargs):
    if controller_type == "gpio":
        pin = kwargs["pin"]
        key = ("gpio", pin)
        if key not in _controller_cache:
            _controller_cache[key] = GPIOController()
        return _controller_cache[key]

    elif controller_type == "pca9685":
        address = kwargs.get("address", 0x40)
        key = ("pca9685", address)
        if key not in _controller_cache:
            _controller_cache[key] = PCA9685Controller(address)
        return _controller_cache[key]

    else:
        raise ValueError(f"Unsupported controller type: {controller_type}")

def get_matrix_config(path: str | Path) -> List[Dict[str, Any]]:
    with open(path, "r") as f:
        raw_config = json.load(f)

    config = []
    for entry in raw_config:
        controller_type = entry.get("type")
        controller = get_controller(controller_type, **entry)
        config.append({
            "row": entry["row"],
            "col": entry["col"],
            "controller": controller
        })

    return config
