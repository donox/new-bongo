"""
run_tests.py
A simple script to discover and run all unit tests in the 'tests' directory.
"""

import unittest
import os
import sys
from __init__ import setpath
setpath()

# # --- START OF GLOBAL PATH ADJUSTMENT ---
# # Get the directory of the current script (e.g., .../BongoNew/src/tests/)
current_script_dir = os.path.dirname(os.path.abspath(__file__))
#
# # Calculate the path to the 'src' directory (e.g., .../BongoNew/src/)
# # This means going up one level from 'tests'
# src_directory = os.path.abspath(os.path.join(current_script_dir, os.pardir))
#
# # Add the 'src' directory to the beginning of sys.path
# # This makes 'src' directly importable as a top-level package.
# # So 'from src.hardware.abstract_led' will work.
# if src_directory not in sys.path:
#     sys.path.insert(0, src_directory)
#
# print("sys.path after adjustments:")
# for p in sys.path:
#     print(f"  {p}")
# print("-" * 30)
# # --- END OF GLOBAL PATH ADJUSTMENT ---


def run_all_tests():
    # Discover tests in the 'tests' directory
    loader = unittest.TestLoader()
    # Ensure discover starts from the current_script_dir (tests/)
    # This tells unittest where to look for test_*.py files.
    suite = loader.discover(current_script_dir, pattern="test_*.py")

    # Run the tests
    print("Running all Bongo unit tests...\n")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    print("\nAll tests finished.")


if __name__ == '__main__':
    run_all_tests()