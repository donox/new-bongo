# patterns/builtin_patterns.py

import time

def chase(matrix, stop_event, delay=0.1):
    """Turn on LEDs in sequence, then off."""
    while not stop_event.is_set():
        for i in range(len(matrix.leds)):
            matrix.on(i)
            time.sleep(delay)
            matrix.off(i)
            if stop_event.is_set():
                break

def fade_all(matrix, stop_event, steps=10, delay=0.05):
    """Fade all LEDs up and down together."""
    while not stop_event.is_set():
        for level in range(steps):
            brightness = level / steps
            for i in range(len(matrix.leds)):
                matrix.set_brightness(i, brightness)
            time.sleep(delay)
            if stop_event.is_set():
                return

        for level in reversed(range(steps)):
            brightness = level / steps
            for i in range(len(matrix.leds)):
                matrix.set_brightness(i, brightness)
            time.sleep(delay)
            if stop_event.is_set():
                return

def wave_row(matrix, stop_event, rows=3, delay=0.1):
    """Turn on LEDs row-by-row like a wave."""
    while not stop_event.is_set():
        for r in range(rows):
            for c in range(16):  # Adjust if matrix has more/less cols
                matrix.on_at(r, c)
            time.sleep(delay)
            for c in range(16):
                matrix.off_at(r, c)
            if stop_event.is_set():
                return
