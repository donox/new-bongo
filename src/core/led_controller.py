"""
led_controller.py
Defines the LEDController class, which manages a collection of IndividualLED objects
and provides methods to apply patterns or individual commands.
"""

from typing import List, Dict, Tuple, Callable, Generator
import time

from src.core.individual_led import IndividualLED
from src.core.led_commands import LEDOperation
from src.hardware.abstract_led import AbstractLED
from src.hardware.pca9685_led import cleanup_pi_pwm # Import for cleanup if using PiPWMLED


class LEDController:
    """
    Manages a collection of IndividualLED objects. It is responsible for:
    - Initializing and storing LED instances.
    - Starting and stopping all LED worker threads.
    - Distributing LEDOperation commands from patterns to individual LED queues.
    """
    def __init__(self, led_map: Dict[str, AbstractLED]):
        """
        Initializes the LEDController.
        :param led_map: A dictionary where keys are unique LED IDs (e.g., "LED_0_0")
                        and values are initialized AbstractLED instances.
        """
        if not isinstance(led_map, dict) or not all(isinstance(k, str) and isinstance(v, AbstractLED) for k, v in led_map.items()):
            raise TypeError("led_map must be a dictionary of {str: AbstractLED} instances.")

        self.leds: Dict[str, IndividualLED] = {}
        for led_id, hw_led_instance in led_map.items():
            self.leds[led_id] = IndividualLED(hw_led_instance, led_id)

        self._num_leds = len(self.leds)
        print(f"LEDController initialized with {self._num_leds} LEDs.")

    def start_all_led_threads(self):
        """Starts the worker thread for each individual LED."""
        for led in self.leds.values():
            led.start()
        print(f"All {self._num_leds} LED worker threads started.")

    def stop_all_led_threads(self):
        """
        Stops all individual LED threads and performs any necessary hardware cleanup.
        """
        print(f"Stopping all {self._num_leds} LED worker threads...")
        for led in self.leds.values():
            led.stop()
        print("All LED worker threads stopped.")

        # Perform cleanup for specific hardware types if necessary
        # This is a bit coarse, ideally individual hardware objects would handle their own cleanup
        # but for RPi.GPIO (PiPWMLED), a global cleanup is often needed.
        try:
            cleanup_pi_pwm() # Call the cleanup function from pi_pwm_led.py
        except NameError:
            # If pi_pwm_led was not imported or cleanup_pi_pwm doesn't exist
            pass
        except Exception as e:
            print(f"Error during hardware cleanup: {e}")


    def clear_all_led_operations(self):
        """Clears all pending operations for all managed LEDs."""
        print("Clearing all pending LED operations...")
        for led in self.leds.values():
            led.clear_pending_operations()
        print("All pending LED operations cleared.")

    def apply_pattern_commands(self, pattern_generator: Generator[Tuple[str, LEDOperation], None, None]):
        """
        Takes a pattern generator that yields (led_id, LEDOperation) tuples
        and adds them to the respective LED's command queue.
        """
        print("Applying pattern commands from generator...")
        commands_applied = 0
        for led_id, operation in pattern_generator:
            if led_id in self.leds:
                self.leds[led_id].add_operation(operation)
                commands_applied += 1
            else:
                print(f"Warning: Command for unknown LED ID '{led_id}'. Skipping.")
        print(f"Applied {commands_applied} pattern commands to queues.")

    def get_led_brightness(self, led_id: str) -> int:
        """
        Returns the current brightness of a specific LED.
        Useful for visualization or debugging.
        """
        if led_id in self.leds:
            return self.leds[led_id].get_current_brightness()
        raise ValueError(f"LED with ID '{led_id}' not found.")