# new-bongo/src/bongo/patterns/base_patterns.py

import time
import random
from typing import Generator, Tuple, List

from bongo.operations.led_operation import LEDOperation
from bongo.utils.constants import BRIGHTNESS_MAX, BRIGHTNESS_MIN

def create_wave_pattern(led_coords: List[Tuple[int, int]], start_time_base: float = 0) -> Generator[
    Tuple[Tuple[int, int], LEDOperation], None, None]:
    """
    Generates LEDOperations for a sequential "wave" effect across given LEDs.
    The wave progresses based on the order of led_coords provided.
    
    :param led_coords: A list of (row, col) tuples representing the LEDs in the order
                       the wave should propagate.
    :param start_time_base: The base time (time.monotonic()) from which delays are calculated.
    :return: A generator yielding ((row, col), LEDOperation) tuples.
    """
    print("Generating wave pattern commands...")
    
    # Example parameters for the wave effect
    ramp_time = 0.1
    hold_time = 0.3
    fade_time = 0.4
    stagger_delay_per_led = 0.1  # Time difference between consecutive LEDs in the wave

    for i, coords in enumerate(led_coords):
        # Stagger the start time for each LED
        staggered_start = start_time_base + (i * stagger_delay_per_led)

        operation = LEDOperation(
            start_time=staggered_start,
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=ramp_time,
            hold_duration=hold_time,
            fade_duration=fade_time
        )
        yield (coords, operation)

    # def __init__(self, channel: int, on_value: int, off_value: int):
    #     """
    #     Initializes a direct hardware operation.
    #
    #     Args:
    #         channel: The specific hardware channel (0-15 for PCA9685).
    #         on_value: The PWM tick (0-4095) to turn the signal on.
    #         off_value: The PWM tick (0-4095) to turn the signal off.
    #     """

def create_random_flash_pattern(led_coords: List[Tuple[int, int]], num_flashes: int, start_time_base: float = 0) -> Generator[
    Tuple[Tuple[int, int], LEDOperation], None, None]:
    """
    Generates LEDOperations for random LEDs to flash with varying characteristics.
    
    :param led_coords: A list of (row, col) tuples representing the available LEDs.
    :param num_flashes: The total number of flash operations to generate.
    :param start_time_base: The base time (time.monotonic()) from which random delays are added.
    :return: A generator yielding ((row, col), LEDOperation) tuples.
    """
    if not led_coords:
        return  # No LEDs to flash

    print(f"Generating {num_flashes} random flash commands...")
    for _ in range(num_flashes):
        random_led_coords = random.choice(led_coords)
        random_delay = random.uniform(0, 2.0)  # Random delay for flash start

        operation = LEDOperation(
            start_time=start_time_base + random_delay,
            target_brightness=random.randint(BRIGHTNESS_MIN + 50, BRIGHTNESS_MAX),  # Avoid pure black flash
            ramp_duration=random.uniform(0.05, 0.2),
            hold_duration=random.uniform(0.1, 0.4),
            fade_duration=random.uniform(0.2, 0.6)
        )
        yield (random_led_coords, operation)


def create_blink_pattern(led_coords: Tuple[int, int], num_blinks: int, interval: float, start_time_base: float = 0) -> Generator[
    Tuple[Tuple[int, int], LEDOperation], None, None]:
    """
    Generates LEDOperations for a single LED to blink multiple times.
    
    :param led_coords: The (row, col) tuple of the single LED to blink.
    :param num_blinks: The number of times the LED should blink (on-off cycle).
    :param interval: The duration for each "on" phase and each "off" phase (e.g., 0.5s on, 0.5s off).
    :param start_time_base: The base time (time.monotonic()) for the pattern to start.
    :return: A generator yielding ((row, col), LEDOperation) tuples.
    """
    print(f"Generating {num_blinks} blink commands for {led_coords}...")
    current_start_time = start_time_base
    for _ in range(num_blinks):
        # On operation
        on_op = LEDOperation(
            start_time=current_start_time,
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=0.05,  # Quick ramp up
            hold_duration=interval - 0.10, # Hold duration adjusted for ramp/fade
            fade_duration=0.05   # Quick fade down
        )
        yield (led_coords, on_op)
        
        # Move start time for next blink
        current_start_time += interval * 2 # One interval for ON, one for OFF