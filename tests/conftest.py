import pytest
from bongo.matrix.matrix import LEDMatrix

@pytest.fixture
def mock_matrix():
    config = [
        {"row": 0, "col": 0, "type": "mock", "pin": 1},
        {"row": 0, "col": 1, "type": "mock", "pin": 2},
        {"row": 1, "col": 0, "type": "mock", "pin": 3},
        {"row": 1, "col": 1, "type": "mock", "pin": 4},
    ]
    return LEDMatrix(config=config)
