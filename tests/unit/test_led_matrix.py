import pytest
from bongo.matrix.matrix import LEDMatrix
from unittest.mock import Mock

@pytest.fixture
def mock_controller():
    return Mock()

@pytest.fixture
def matrix(mock_controller):
    matrix = LEDMatrix()
    matrix.initialize(2, 2, mock_controller)
    return matrix

def test_matrix_initialization(matrix, mock_controller):
    assert matrix._rows == 2
    assert matrix._cols == 2
    assert matrix._controller == mock_controller

def test_matrix_on_calls_controller(matrix, mock_controller):
    matrix.on(0, 1)
    mock_controller.set_pixel.assert_called_with(0, 1, 255, 255, 255, brightness=1.0)

def test_matrix_off_calls_controller(matrix, mock_controller):
    matrix.off(1, 0)
    mock_controller.set_pixel.assert_called_with(1, 0, 0, 0, 0, brightness=0.0)
