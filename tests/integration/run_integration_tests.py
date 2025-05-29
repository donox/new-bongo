#!/usr/bin/env python3
"""
Run integration tests only (real hardware, GPIO/PCA9685).
Accepts an optional argument specifying a test to run:
    python3 -m run_integration_tests                   # runs all integration tests
    python3 -m run_integration_tests test_file.py      # runs all tests in test_file.py
    python3 -m run_integration_tests test_file.py::TestClass::test_method  # runs one specific test
"""

import sys
import pytest
from pathlib import Path

print("Running integration tests (real hardware)...")

# Compute project root (2 levels up from this file)
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

# Add src/ to sys.path so 'bongo' package can be imported
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Determine what to run
if len(sys.argv) > 1:
    # Allow flexible specification like test file or test function
    test_target = sys.argv[1]
    if not test_target.startswith("tests/"):
        test_target = str(project_root / "tests/integration" / test_target)
    pytest_args = [test_target]
else:
    # Default: run all integration tests
    pytest_args = [str(project_root / "tests/integration")]

# Run pytest with the specified arguments
pytest.main(pytest_args)
