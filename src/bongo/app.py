"""
app.py
Main entry point for the Bongo LED control system.
Handles setup, command-line arguments, and runs patterns.
"""

import time
import argparse

from bongo.matrix.basic_matrix import BasicLEDMatrix
from bongo.hardware.mock_hal import MockPixelController
from bongo.operations.animation_manager import AnimationManager
from bongo.operations.patterns import (
    create_wave_pattern,
    create_random_flash_pattern,
    create_blink_pattern
)

# Optional hardware controllers
try:
    from bongo.hardware.pca9685_hal import PCA9685PixelController
    HAS_PCA9685 = True
except ImportError:
    HAS_PCA9685 = False

try:
    from bongo.hardware.rpi_gpio_hal import RPiGPIOPixelController
    HAS_RPI_GPIO = True
except ImportError:
    HAS_RPI_GPIO = False


def setup_controller(controller_type: str, rows: int, cols: int):
    """
    Initializes and returns a tuple of (matrix, controller) for the chosen hardware type.
    """
    if controller_type == "mock":
        pixel_controller = MockPixelController(rows, cols)
    elif controller_type == "pca9685":
        if not HAS_PCA9685:
            raise RuntimeError("PCA9685 controller not available.")
        pixel_controller = PCA9685PixelController(rows, cols)
    elif controller_type == "gpio":
        if not HAS_RPI_GPIO:
            raise RuntimeError("RPiGPIO controller not available.")
        # GPIO pins must be passed manually or configured via settings
        gpio_pins = list(range(12, 12 + rows * cols))  # Example
        pixel_controller = RPiGPIOPixelController(rows, cols, gpio_pins)
    else:
        raise ValueError(f"Unknown controller type: {controller_type}")

    matrix = BasicLEDMatrix()
    matrix.initialize(rows, cols, pixel_controller)
    return matrix, pixel_controller


def run():
    parser = argparse.ArgumentParser(description="Bongo LED Control System")
    parser.add_argument('--controller', type=str, default='mock',
                        choices=['mock', 'pca9685', 'gpio'],
                        help='Choose controller: mock, pca9685, or gpio.')
    parser.add_argument('--pattern', type=str, default='wave',
                        choices=['wave', 'random_flash', 'blink_single'],
                        help='Choose a pattern to run.')
    parser.add_argument('--rows', type=int, default=2,
                        help='Number of rows in the LED matrix.')
    parser.add_argument('--cols', type=int, default=2,
                        help='Number of columns in the LED matrix.')
    parser.add_argument('--duration', type=int, default=10,
                        help='How long to run the animation (in seconds).')
    parser.add_argument('--blink-row', type=int, default=0,
                        help='Row index of LED to blink (for blink_single).')
    parser.add_argument('--blink-col', type=int, default=0,
                        help='Col index of LED to blink (for blink_single).')

    args = parser.parse_args()

    try:
        matrix, controller = setup_controller(args.controller, args.rows, args.cols)
    except Exception as e:
        print(f"Error initializing controller: {e}")
        return

    manager = AnimationManager(matrix, controller)
    manager.start()

    led_coords = [(r, c) for r in range(args.rows) for c in range(args.cols)]
    start_time = time.monotonic()

    if args.pattern == 'wave':
        pattern = create_wave_pattern(led_coords, start_time_base=start_time)
    elif args.pattern == 'random_flash':
        pattern = create_random_flash_pattern(led_coords, num_flashes=10, start_time_base=start_time)
    elif args.pattern == 'blink_single':
        target = (args.blink_row, args.blink_col)
        pattern = create_blink_pattern(target, num_blinks=5, interval=0.5, start_time_base=start_time)
    else:
        print("Unknown pattern selected.")
        return

    manager.apply_pattern_commands(pattern)

    try:
        print(f"Running pattern '{args.pattern}' for {args.duration} seconds...")
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        print("Stopping animation and clearing display...")
        manager.stop()
        matrix.clear()
        matrix.refresh()
        controller.shutdown()


if __name__ == "__main__":
    run()
