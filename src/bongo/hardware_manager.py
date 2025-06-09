# src/bongo/hardware_manager.py
from typing import Dict

# --- For testing on a non-Pi machine vs. real hardware ---
try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685

    IS_PI = True
except (NotImplementedError, ModuleNotFoundError):
    print("⚠️  Could not import hardware libraries. Assuming not on a Raspberry Pi.")
    IS_PI = False


    # Define placeholder classes so the code doesn't crash on import
    # on a non-Pi machine.
    class PCA9685:
        pass


class HardwareManager:
    """
    Manages and provides access to all hardware resources, such as the I2C bus
    and the PCA9685 controllers. This is a singleton-like pattern to ensure
    hardware is initialized only once.
    """

    def __init__(self, addresses: list[int]):
        """
        Initializes the I2C bus and all PCA9685 controllers.

        Args:
            addresses: A list of I2C addresses for all PCA9685 boards.
        """
        print("\n[INSTRUMENTATION] ==> Initializing REAL HardwareManager...")

        self.i2c_bus = None
        self.controllers: Dict[int, PCA9685] = {}

        if not IS_PI:
            print("[INSTRUMENTATION]     - Not on a Pi. Skipping real hardware setup.")
            return

        try:
            print("[INSTRUMENTATION]     - Initializing I2C bus...")
            self.i2c_bus = busio.I2C(board.SCL, board.SDA)
            print("[INSTRUMENTATION]     - I2C bus initialized.")

            for addr in addresses:
                print(f"[INSTRUMENTATION]     - Initializing REAL PCA9685 at address {hex(addr)}...")
                self.controllers[addr] = PCA9685(self.i2c_bus, address=addr)
            print("[INSTRUMENTATION]     - All REAL hardware controllers initialized.")
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize hardware: {e}")
            raise

    def get_controller(self, address: int) -> PCA9685:
        """
        Retrieves a pre-initialized PCA9685 controller instance.
        """
        print(f"[INSTRUMENTATION] ==> REAL HardwareManager.get_controller() called for address: {hex(address)}")
        controller = self.controllers.get(address)
        if controller is None:
            raise ValueError(f"No controller found for address {hex(address)}. Was it initialized?")
        return controller
