import pytest
from bongo.operations.led_operation import LEDPixelOperation
from conftest import mock_matrix


@pytest.fixture
def matrix(mock_matrix):
    return mock_matrix


class TestLEDPixelOperation:

    def test_turn_on_single_pixel(self, matrix):
        op = LEDPixelOperation(row=0, col=0, on=True)
        op.apply(matrix)
        assert matrix.get_pixel(0, 0) == 255

    def test_turn_off_single_pixel(self, matrix):
        matrix.set_pixel(0, 0, 255)
        op = LEDPixelOperation(row=0, col=0, on=False)
        op.apply(matrix)
        assert matrix.get_pixel(0,0) == 0

