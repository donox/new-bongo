from abc import ABC, abstractmethod

class ILEDMatrix(ABC):
    @abstractmethod
    def on(self, index: int): pass

    @abstractmethod
    def off(self, index: int): pass

    @abstractmethod
    def set_brightness(self, index: int, value: float): pass
