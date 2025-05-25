"""
main.py
Main entry point for the Bongo LED control system.
Handles setup, command-line arguments, and runs patterns.
"""

import time
import argparse
from typing import Dict

# Import core components
from src.core.led_controller import LEDController
from src.core.led_commands import LEDOperation
from src.patterns.base_patterns import create_wave_pattern, create_random_flash_pattern, create_blink_pattern

# Import hardware implementations
from src.hardware.abstract_led import AbstractLED
from src.hardware.mock_led import MockLED

# Conditional imports for real hardware:
try:
    from src.hardware.pca9685_led import PCA9685LED, get_pca9685_board

    HAS_PCA9685 = True
except (ImportError, RuntimeError) as e:
    print(f"Warning: Could not import PCA9685LED ({e}). PCA9685 hardware will not be available.")
    HAS_PCA9685 = False

try:
    from src.hardware.pi_pwm_led import PiPWMLED, cleanup_pi_pwm

    HAS_PI_PWM = True
except (ImportError, RuntimeError) as e:
    print(f"Warning: Could not import PiPWMLED ({e}). Raspberry Pi hardware PWM will not be available.")
    HAS_PI_PWM = False


def setup_leds(use_mock_hardware: bool) -> Dict[str, AbstractLED]:
    """
    Sets up and returns a dictionary of AbstractLED instances based on
    whether mock hardware is requested or actual hardware is available.
    """
    led_map: Dict[str, AbstractLED] = {}

    if use_mock_hardware:
        print("Setting up with MockLEDs for testing.")
        # Define some mock LEDs
        for i in range(4):  # Example: 4 mock LEDs
            led_id = f"mock_led_{i}"
            led_map[led_id] = MockLED(led_id)
        # You can add more mock LEDs with specific IDs if needed
        led_map["mock_led_special"] = MockLED("mock_led_special")
    else:
        print("Attempting to set up with real hardware.")
        # --- Configure your real LEDs here ---
        # This is where you map your physical LEDs to software objects.
        # Example: 2 LEDs on PCA9685, 1 LED on Pi PWM

        # PCA9685 LEDs
        if HAS_PCA9685:
            try:
                # Ensure PCA9685 board is initialized
                pca_board_0x40 = get_pca9685_board(i2c_address=0x40)  # Default address
                # You can call get_pca9685_board for other addresses if daisy-chained
                # pca_board_0x41 = get_pca9685_board(i2c_address=0x41)

                led_map["pca_led_0"] = PCA9685LED("pca_led_0", pca_channel=0, pca_address=0x40)
                led_map["pca_led_1"] = PCA9685LED("pca_led_1", pca_channel=1, pca_address=0x40)
                # Add more as needed
            except RuntimeError as e:
                print(f"Error setting up PCA9685 LEDs: {e}")
                print("Skipping PCA9685 LED setup.")
        else:
            print("PCA9685 support not available. Skipping PCA9685 LED setup.")

        # Pi PWM LEDs
        if HAS_PI_PWM:
            try:
                # IMPORTANT: Replace with your actual GPIO pin numbers that support hardware PWM
                # Standard hardware PWM pins: GPIO12, GPIO13, GPIO18, GPIO19
                led_map["pi_pwm_led_0"] = PiPWMLED("pi_pwm_led_0", gpio_pin=12)  # Example: GPIO12
                # led_map["pi_pwm_led_1"] = PiPWMLED("pi_pwm_led_1", gpio_pin=13) # Example: GPIO13
                # Add more as needed
            except Exception as e:
                print(f"Error setting up PiPWM LEDs: {e}")
                print("Skipping PiPWM LED setup.")
        else:
            print("Raspberry Pi hardware PWM support not available. Skipping PiPWM LED setup.")

        if not led_map:
            print("No real LEDs were set up. Consider using --mock for testing.")
            # Fallback to mock if no real hardware can be initialized
            return setup_leds(use_mock_hardware=True)

    return led_map


def main():
    parser = argparse.ArgumentParser(description="Bongo LED Control System")
    parser.add_argument('--mock', action='store_true',
                        help='Use mock hardware for testing instead of actual GPIO/PCA9685.')
    parser.add_argument('--pattern', type=str, default='wave',
                        choices=['wave', 'random_flash', 'blink_single', 'off'],
                        help='Choose a pattern to run (wave, random_flash, blink_single, off).')
    parser.add_argument('--duration', type=int, default=10,
                        help='Duration in seconds to run the pattern (default: 10).')
    parser.add_argument('--blink-led', type=str, default='mock_led_0',
                        help='For "blink_single" pattern, specify the LED ID to blink (e.g., "mock_led_0", "pca_led_0").')

    args = parser.parse_args()

    # Setup LEDs based on argument
    led_map = setup_leds(args.mock)
    if not led_map:
        print("No LEDs configured. Exiting.")
        return

    controller = LEDController(led_map)

    try:
        controller.start_all_led_threads()
        time.sleep(0.5)  # Give threads a moment to start

        if args.pattern == 'wave':
            # Create a list of all LED IDs for the wave pattern
            all_led_ids = list(led_map.keys())
            controller.apply_pattern_commands(create_wave_pattern(all_led_ids, time.monotonic()))
        elif args.pattern == 'random_flash':
            all_led_ids = list(led_map.keys())
            controller.apply_pattern_commands(
                create_random_flash_pattern(all_led_ids, num_flashes=20, start_time_base=time.monotonic()))
        elif args.pattern == 'blink_single':
            if args.blink_led not in led_map:
                print(f"Error: LED ID '{args.blink_led}' not found for blinking pattern.")
            else:
                controller.apply_pattern_commands(
                    create_blink_pattern(args.blink_led, num_blinks=5, interval=1.0, start_time_base=time.monotonic()))
        elif args.pattern == 'off':
            print("Turning all LEDs off and clearing commands.")
            controller.clear_all_led_operations()
            for led_id in led_map.keys():
                # Ensure they are explicitly off after clearing operations
                if led_id in controller.leds:
                    controller.leds[led_id]._hw_led.off()

        print(f"\nRunning pattern '{args.pattern}' for {args.duration} seconds...")
        time.sleep(args.duration)

    except KeyboardInterrupt:
        print("\nCtrl+C detected. Initiating graceful shutdown...")
    finally:
        controller.stop_all_led_threads()
        print("Bongo LED Control System stopped.")


if __name__ == "__main__":
    main()