# tests/conftest.py
import pytest
from unittest.mock import MagicMock

# Assuming LEDMatrix is in src.bongo.matrix.matrix
from src.bongo.matrix.matrix import LEDMatrix


# Assuming you have a mock PCA9685 class for testing,
# e.g., in src.bongo.controller.mock_pca9685.py
# If not, we can define a simple MagicMock for the class here.
# For robust testing, having a dedicated MockPCA9685 class is good.
# Let's assume one exists or create a suitable mock on the fly.

# If you have a specific MockPCA9685 class:
# from src.bongo.controller.mock_pca9685 import MockPCA9685
# For now, let's create a generic MagicMock to act as the class factory
# This mock_pca_class_factory will be passed to LEDMatrix
@pytest.fixture
def mock_pca_class_factory():
    """
    Provides a MagicMock that simulates a PCA9685 class factory.
    When this mock is called (instantiated), it returns another MagicMock (the instance).
    """
    mock_pca_instance = MagicMock(name="MockPCA9685Instance")
    # Configure the instance mock if methods like set_pwm_freq need to exist
    mock_pca_instance.set_pwm_freq = MagicMock()
    mock_pca_instance.set_pwm = MagicMock()
    mock_pca_instance.set_all_pwm = MagicMock()

    class_factory = MagicMock(name="MockPCA9685ClassFactory", return_value=mock_pca_instance)
    return class_factory


@pytest.fixture
def mock_matrix(mock_pca_class_factory):  # Inject the factory
    """
    Provides a mock LEDMatrix instance for tests that need it.
    """
    # This config needs to be compatible with how LEDMatrix uses it
    # to instantiate HybridLEDController.
    # HybridLEDController expects 'controller_address' and 'led_channel'.
    # The original 'pin' needs to map to 'led_channel'.
    # We also need 'controller_address' for each.
    config = [
        {"row": 0, "col": 0, "controller_address": 0x40, "led_channel": 1, "type": "mock"},
        {"row": 0, "col": 1, "controller_address": 0x40, "led_channel": 2, "type": "mock"},
        {"row": 1, "col": 0, "controller_address": 0x40, "led_channel": 3, "type": "mock"},
        {"row": 1, "col": 1, "controller_address": 0x40, "led_channel": 4, "type": "mock"},
    ]
    # Now, when LEDMatrix is initialized, pass the mock_pca_class_factory
    # This factory will be used by HybridLEDController instances created by LEDMatrix.
    matrix = LEDMatrix(config=config, default_pca9685_class=mock_pca_class_factory)
    return matrix

# Add other global fixtures if needed
