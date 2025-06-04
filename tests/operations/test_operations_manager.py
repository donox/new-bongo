import pytest
from bongo.operations.animation_manager import AnimationManager
from conftest import mock_matrix


@pytest.fixture
def matrix(mock_matrix):
    return mock_matrix


@pytest.fixture
def manager(matrix):
    return AnimationManager(matrix, pixel_controller=None)


class DummyOperation:
    def __init__(self, calls):
        self.calls = calls

    def update(self, time_now):
        self.calls.append("op_called")
        return True


def test_add_operation_and_tick(manager):
    calls = []
    op = DummyOperation(calls)
    manager.add_operation(op)
    manager.tick(0.0)
    assert "op_called" in calls


def test_clear_operations(manager):
    calls = []
    op = DummyOperation(calls)
    manager.add_operation(op)
    manager.clear_operations()
    manager.tick(0.0)
    assert "op_called" not in calls


def test_multiple_operations_called(manager):
    calls = []

    class Op:
        def update(self, time_now):
            calls.append("called")
            return True

    op1 = Op()
    op2 = Op()

    manager.add_operation(op1)
    manager.add_operation(op2)
    manager.tick(0.0)
    assert calls.count("called") == 2
