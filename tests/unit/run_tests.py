#!/usr/bin/env python3
"""
Run unit tests only (mocked hardware).
"""

import sys
from pathlib import Path
import pytest

# Add src/ to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

# Run tests
if __name__ == "__main__":
    print("Running unit tests (mocked hardware)...")
    sys.exit(pytest.main(["tests/unit", "-x"]))
