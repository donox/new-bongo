# REPLACEMENT MODULE: run_operations_tests.py

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

def is_running_on_pi():
    """Basic check to see if we’re on a Raspberry Pi."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except Exception:
        return False

def main():
    use_real_hardware = os.getenv("USE_REAL_HARDWARE") == "1"

    if use_real_hardware:
        print("🟢 Running tests with REAL hardware (USE_REAL_HARDWARE=1)")
    else:
        print("🧪 Running tests with MOCKED hardware (USE_REAL_HARDWARE=0 or unset)")

    # Optional safety check: warn if using real hardware on a non-Pi
    if use_real_hardware and not is_running_on_pi():
        print("⚠️ WARNING: USE_REAL_HARDWARE is set, but this does not appear to be a Raspberry Pi.")
        print("           Tests may fail unless running on compatible hardware.")

    # Run all tests in this directory (test_operations_manager, etc.)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    result_code = pytest.main([test_dir])

    sys.exit(result_code)

if __name__ == "__main__":
    main()
