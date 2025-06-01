# patterns/json_loader.py

import json
import os

def load_pattern(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Pattern file '{file_path}' does not exist.")

    with open(file_path, 'r') as f:
        data = json.load(f)

    # Basic validation
    if "steps" not in data or not isinstance(data["steps"], list):
        raise ValueError("Invalid pattern file: must contain a list of 'steps'.")

    return data["steps"], data.get("loop", False)
