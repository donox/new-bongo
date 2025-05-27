#!/usr/bin/env python3
"""
Run integration tests only (real hardware, GPIO/PCA9685).
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

# Run the integration tests using full path
pytest.main([str(project_root / "tests/integration")])

