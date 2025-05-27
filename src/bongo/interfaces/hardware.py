from abc import ABC, abstractmethod


class IPixelController(ABC):
    """
    Interface for a hardware abstraction that controls individual pixels in a grid.
    Implementations may use PWM, I2C (e.g., PCA9685), or mock logic.
    """

    @abstractmethod
    def initialize(self, num_rows: int, num_cols: int, **kwargs) -> None:
        """
        Initialize the controller with a specific matrix size.
        Additional hardware-specific arguments may be passed via kwargs.
        """
        pass

    @abstractmethod
    def set_pixel(self, row: int, col: int, r: int, g: int, b: int, brightness: float = 1.0) -> None:
        """
        Set a single pixel's color and brightness.
        Color is an RGB triplet (0–255), brightness is 0.0–1.0.
        """
        pass

    @abstractmethod
    def show(self) -> None:
        """
        Commit changes to hardware (e.g., update PWM signals).
        Some platforms buffer pixel values until this is called.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Turn off all pixels.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Gracefully shut down the controller, releasing hardware resources.
        """
        pass
