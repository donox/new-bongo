import pytest
import os
from bongo.matrix.matrix import LEDMatrix
from bongo.hardware.mock_hal import MockPixelController
from bongo.operations.operations_manager import OperationsManager

@pytest.fixture
def matrix():
    rows = 2
    cols = 2
    controller = MockPixelController(rows, cols)
    config = [
        {"row": r, "col": c, "controller": controller}
        for r in range(rows) for c in range(cols)
    ]
    return LEDMatrix(config=config)

@pytest.fixture
def manager(matrix):
    return OperationsManager(matrix)

def test_add_operation_and_tick(manager):
    calls = []

    def op(matrix):
        calls.append("op_called")

    manager.add_operation(op)
    manager.tick()

    assert calls == ["op_called"]

def test_clear_operations(manager):
    def op(matrix):
        pass

    manager.add_operation(op)
    manager.clear_operations()
    assert not manager.operations

def test_multiple_operations_called(manager):
    called = []

    def op1(matrix):
        called.append("op1")

    def op2(matrix):
        called.append("op2")

    manager.add_operation(op1)
    manager.add_operation(op2)
    manager.tick()

    assert "op1" in called
    assert "op2" in called
