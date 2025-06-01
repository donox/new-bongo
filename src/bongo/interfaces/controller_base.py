# controller/controller_base.py

class BaseLEDController:
    def on(self):
        raise NotImplementedError

    def off(self):
        raise NotImplementedError

    def set_brightness(self, value: float):
        raise NotImplementedError
