# app.py

import argparse
import time
import signal
import sys

from patterns.pattern_manager import PatternManager
from patterns.json_loader import load_pattern

from config.loader import get_matrix_config
from bongo.matrix.matrix import LEDMatrix

matrix_config = get_matrix_config("config/production_config.json")
matrix = LEDMatrix(config=matrix_config)

pattern_manager = None

def parse_args():
    parser = argparse.ArgumentParser(description="Control hybrid LED matrix.")
    parser.add_argument('--on', type=int, help="Turn on LED by index")
    parser.add_argument('--off', type=int, help="Turn off LED by index")
    parser.add_argument('--brightness', nargs=2, metavar=('INDEX', 'VALUE'),
                        help="Set brightness for LED by index (0.0 to 1.0)")

    parser.add_argument('--on-at', nargs=2, type=int, metavar=('ROW', 'COL'),
                        help="Turn on LED at specific row/col")
    parser.add_argument('--off-at', nargs=2, type=int, metavar=('ROW', 'COL'),
                        help="Turn off LED at specific row/col")
    parser.add_argument('--brightness-at', nargs=3, metavar=('ROW', 'COL', 'VALUE'),
                        help="Set brightness at row/col (0.0 to 1.0)")

    parser.add_argument('--pattern', type=str, help="Run a built-in pattern (e.g., chase)")
    parser.add_argument('--pattern-file', type=str, help="Run a pattern defined in JSON file")

    return parser.parse_args()

def stop_handler(sig, frame):
    print("\nStopping pattern and cleaning up...")
    if pattern_manager:
        pattern_manager.stop()
    if matrix:
        for i in range(len(matrix.leds)):
            matrix.off(i)
    sys.exit(0)

def main():
    global matrix, pattern_manager
    signal.signal(signal.SIGINT, stop_handler)

    args = parse_args()
    matrix = LEDMatrix()
    pattern_manager = PatternManager(matrix)

    # Direct controls
    if args.on is not None:
        matrix.on(args.on)
    if args.off is not None:
        matrix.off(args.off)
    if args.brightness:
        idx, val = int(args.brightness[0]), float(args.brightness[1])
        matrix.set_brightness(idx, val)

    if args.on_at:
        matrix.on_at(*args.on_at)
    if args.off_at:
        matrix.off_at(*args.off_at)
    if args.brightness_at:
        row, col = int(args.brightness_at[0]), int(args.brightness_at[1])
        val = float(args.brightness_at[2])
        matrix.set_brightness_at(row, col, val)

    # Pattern execution
    if args.pattern:
        print(f"Running built-in pattern: {args.pattern}")
        pattern_manager.run_builtin(args.pattern)

    elif args.pattern_file:
        print(f"Running pattern from file: {args.pattern_file}")
        steps, loop = load_pattern(args.pattern_file)
        pattern_manager.run_steps(steps, loop=loop)

    # Keep alive if a pattern is running
    if args.pattern or args.pattern_file:
        print("Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

if __name__ == '__main__':
    main()
