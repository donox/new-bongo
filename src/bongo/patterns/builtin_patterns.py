# src/bongo/patterns/builtin_patterns.py
import time
from typing import List, Tuple
from bongo.operations.led_operation import LEDPixelOperation


def create_chase_pattern(
        led_coords: List[Tuple[int, int]],
        delay: float = 0.1,
        brightness: float = 1.0,
        hold_time: float = 0.05,
        start_time_base: float = None
) -> List[Tuple[Tuple[int, int], LEDPixelOperation]]:
    """
    Creates a chase pattern where LEDs light up in sequence.
    """
    # If no start time provided, use current time
    if start_time_base is None:
        start_time_base = time.monotonic()

    # print(f"DEBUG: Creating chase pattern, start_time_base = {start_time_base}")

    operations = []

    for i, coords in enumerate(led_coords):
        # Each LED starts after the previous one by 'delay' seconds
        led_start_time = start_time_base + (i * delay)

        # print(f"DEBUG: LED {i} at {coords} -> start_time = {led_start_time} (offset: {i * delay})")

        pixel_op = LEDPixelOperation(
            target_brightness=brightness,
            ramp_duration=0.02,  # Quick ramp up
            hold_duration=hold_time,
            fade_duration=0.08,  # Quick fade out
            start_time=led_start_time,  # Specific start time for this LED
            initial_brightness=0.0
        )
        operations.append((coords, pixel_op))

    # print(f"DEBUG: Created {len(operations)} operations")
    return operations


def create_fade_all_pattern(
        led_coords: List[Tuple[int, int]],
        fade_up_duration: float = 0.5,
        hold_duration: float = 1.0,
        fade_down_duration: float = 0.5,
        brightness: float = 1.0,
        start_time_base: float = None
) -> List[Tuple[Tuple[int, int], LEDPixelOperation]]:
    """
    Creates a pattern where all LEDs fade up and down together.
    """
    if start_time_base is None:
        start_time_base = time.monotonic()

    operations = []
    for coords in led_coords:
        pixel_op = LEDPixelOperation(
            target_brightness=brightness,
            ramp_duration=fade_up_duration,
            hold_duration=hold_duration,
            fade_duration=fade_down_duration,
            start_time=start_time_base
        )
        operations.append((coords, pixel_op))

    return operations


def create_wave_row_pattern(
        led_coords: List[Tuple[int, int]],
        row_delay: float = 0.1,
        brightness: float = 1.0,
        hold_time: float = 0.2,
        start_time_base: float = None
) -> List[Tuple[Tuple[int, int], LEDPixelOperation]]:
    """
    Creates a wave pattern that moves row by row.
    """
    if start_time_base is None:
        start_time_base = time.monotonic()

    # Group coordinates by row
    rows = {}
    for coords in led_coords:
        row = coords[0]
        if row not in rows:
            rows[row] = []
        rows[row].append(coords)

    operations = []
    for row_num in sorted(rows.keys()):
        row_coords = rows[row_num]
        start_time = start_time_base + (row_num * row_delay)

        for coords in row_coords:
            pixel_op = LEDPixelOperation(
                target_brightness=brightness,
                ramp_duration=0.05,
                hold_duration=hold_time,
                fade_duration=0.1,
                start_time=start_time
            )
            operations.append((coords, pixel_op))

    return operations