# integration/run_integration_tests.py

import unittest
import os
import sys
from __init__ import setpath
setpath()

def run_all_integration_tests():
    print("--- Starting Bongo Integration Tests ---")

    try:
        import RPi.GPIO as GPIO
        from bongo.hardware.rpi_gpio_hal import PiPWMLED, cleanup_pi_pwm, _pwm_objects

        GPIO_AVAILABLE = True
    except (ImportError, RuntimeError) as e:
        GPIO_AVAILABLE = False
        print(f"Skipping PiPWMLED integration tests: RPi.GPIO not available or setup issue: {e}")
        print(f"TOPDEBUG: Import error details: {e.args}")  # More verbose error
        print(f"TOPDEBUG: Attempting to import 'src.hardware.pi_pwm_led' failed. sys.path: {sys.path}")

    # Get the directory of the current script (e.g., .../BongoNew/integration/)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # Calculate the path to the 'src' directory (e.g., .../BongoNew/src/)
    project_root = os.path.abspath(os.path.join(current_script_dir, os.pardir, os.pardir))
    src_directory = os.path.abspath(os.path.join(project_root, 'src'))

    # Add the 'src' directory to the beginning of sys.path
    # This makes 'src' directly importable as a top-level package.
    if src_directory not in sys.path:
        sys.path.insert(0, src_directory)

    # print("sys.path for integration tests:")
    # for p in sys.path:
    #     print(f"  {p}")
    # print("-" * 30)

    # Discover tests in the 'integration' directory
    loader = unittest.TestLoader()
    suite = loader.discover(current_script_dir, pattern="test_*.py")

    # Run the tests
    print("\nRunning all Bongo integration tests...\n")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    print("\nAll integration tests finished.")

if __name__ == '__main__':
    run_all_integration_tests()