# REPLACEMENT MODULE: run_matrix_tests.py

import os
import sys
import pytest

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
        print("🟢 Running matrix tests with REAL hardware (USE_REAL_HARDWARE=1)")
    else:
        print("🧪 Running matrix tests with MOCKED hardware (USE_REAL_HARDWARE=0 or unset)")

    if use_real_hardware and not is_running_on_pi():
        print("⚠️ WARNING: USE_REAL_HARDWARE is set, but this does not appear to be a Raspberry Pi.")
        print("           Tests may fail unless running on compatible hardware.")

    test_dir = os.path.dirname(os.path.abspath(__file__))
    result_code = pytest.main([test_dir])

    sys.exit(result_code)

if __name__ == "__main__":
    main()
