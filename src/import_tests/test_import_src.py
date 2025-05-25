# /home/bongo/lights/test_import_src.py

import os
import sys


print("--- Simple Src Import Test ---")

# Calculate the path to the 'src' directory from this script's location
# This script is at /home/bongo/lights/
# The src directory is at /home/bongo/lights/src
src_directory_path = "/home/bongo/lights/src"

# Add 'src' to sys.path
if src_directory_path not in sys.path:
    sys.path.insert(0, src_directory_path)

print(f"sys.path after adding src: {sys.path}")
print(f"Attempting to import from '{src_directory_path}'...")

try:
    # Attempt to import a module from src.hardware
    from hardware.abstract_led import AbstractLED
    print("SUCCESS: Successfully imported src.hardware.abstract_led!")
    import RPi.GPIO as GPIO
    print("SUCCESS: Successfully imported RPi.GPIO!")
    from hardware.pca9685_led import PCA9685LED, get_pca9685_board, _pca_boards
    print("SUCCESS: Successfully imported from pca9685_led")
    from import_tests.l2_imports import make_call
    print("SUCCESS: Successfully imported from l2_imports")
    # You can even try to instantiate it (if it has no abstract methods or is mockable)
    # If AbstractLED is truly abstract, this will fail. Let's not try instantiation here.
    # We just care if the import itself works.

except ImportError as e:
    print(f"FAILURE: Could not import. Error: {e}")
    print(f"DEBUG: sys.modules contains 'src': {'src' in sys.modules}")
    print(f"DEBUG: sys.modules contains 'src.hardware': {'src.hardware' in sys.modules}")
except Exception as e:
    print(f"An unexpected error occurred during import: {e}")

print("Try Module Imports")
from l2_imports import make_call
make_call()

print("--- Test Finished ---")