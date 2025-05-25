"""
base_patterns.py
Contains example pattern generators that yield (led_id, LEDOperation) tuples.
These patterns do not directly control hardware but define sequences of operations.
"""

import time
import random
from typing import Generator, Tuple

from src.core.led_commands import LEDOperation, BRIGHTNESS_MAX, BRIGHTNESS_MIN


def create_wave_pattern(led_ids: list[str], start_time_base: float = 0) -> Generator[
    Tuple[str, LEDOperation], None, None]:
    """
    Generates LEDOperations for a sequential "wave" effect across given LEDs.
    The wave progresses based on the order of led_ids provided.
    """
    print("Generating wave pattern commands...")
    # Calculate staggered start time based on index in the list
    # Assuming led_ids represents a linear or ordered arrangement

    # Example parameters for the wave effect
    ramp_time = 0.1
    hold_time = 0.3
    fade_time = 0.4
    stagger_delay_per_led = 0.1  # Time difference between consecutive LEDs in the wave

    for i, led_id in enumerate(led_ids):
        # Stagger the start time for each LED
        staggered_start = start_time_base + (i * stagger_delay_per_led)

        operation = LEDOperation(
            start_time=staggered_start,
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=ramp_time,
            hold_duration=hold_time,
            fade_duration=fade_time
        )
        yield (led_id, operation)


def create_random_flash_pattern(led_ids: list[str], num_flashes: int, start_time_base: float = 0) -> Generator[
    Tuple[str, LEDOperation], None, None]:
    """
    Generates LEDOperations for random flashing LEDs.
    """
    if not led_ids:
        return  # No LEDs to flash

    print(f"Generating {num_flashes} random flash commands...")
    for _ in range(num_flashes):
        random_led_id = random.choice(led_ids)
        random_delay = random.uniform(0, 2.0)  # Random delay for flash start

        operation = LEDOperation(
            start_time=start_time_base + random_delay,
            target_brightness=random.randint(BRIGHTNESS_MIN + 50, BRIGHTNESS_MAX),  # Avoid pure black flash
            ramp_duration=random.uniform(0.05, 0.2),
            hold_duration=random.uniform(0.1, 0.4),
            fade_duration=random.uniform(0.2, 0.6)
        )
        yield (random_led_id, operation)


def create_blink_pattern(led_id: str, num_blinks: int, interval: float, start_time_base: float = 0) -> Generator[
    Tuple[str, LEDOperation], None, None]:
    """
    Generates LEDOperations for a single LED to blink multiple times.
    """
    print(f"Generating {num_blinks} blink commands for {led_id}...")
    current_start_time = start_time_base
    for _ in range(num_blinks):
        # On operation
        on_op = LEDOperation(
            start_time=current_start_time,
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=0.05,
            hold_duration=interval / 2,  # Half the interval for ON
            fade_duration=0.05
        )
        yield (led_id, on_op)

        # Move start time for next blink
        current_start_time += interval  # Full interval for next cycle to begin