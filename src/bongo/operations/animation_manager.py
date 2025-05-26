# new-bongo/src/bongo/operations/animation_manager.py

import time
import threading
import queue
from typing import Tuple, Generator, Dict, Optional

# Assuming these interfaces and models are defined or will be defined
from bongo.interfaces.hardware import IPixelController
from bongo.interfaces.matrix import ILEDMatrix  # Assuming ILEDMatrix interface exists
from bongo.interfaces.led import ILED  # For type hinting the LED objects in the matrix
from bongo.operations.led_operation import LEDOperation
from bongo.utils.constants import BRIGHTNESS_MAX, BRIGHTNESS_MIN


class AnimationManager:
    """
    Manages LED animation operations for an entire LED matrix.
    It runs a single dedicated thread to process a queue of LEDOperations,
    updating the logical state of LEDs in an ILEDMatrix and then
    triggering the IPixelController to render these changes to hardware.
    """

    def __init__(self, led_matrix: ILEDMatrix, pixel_controller: IPixelController):
        if not isinstance(led_matrix, ILEDMatrix):
            raise TypeError("led_matrix must be an instance of ILEDMatrix.")
        if not isinstance(pixel_controller, IPixelController):
            raise TypeError("pixel_controller must be an instance of IPixelController.")

        self._led_matrix = led_matrix
        self._pixel_controller = pixel_controller

        # Queue to hold (row, col, LEDOperation) tuples
        self._operation_queue: queue.Queue[Tuple[int, int, LEDOperation]] = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False

        print("AnimationManager: Initialized.")

    def _worker_thread_main(self):
        """
        The main loop for the animation worker thread.
        It continuously processes operations from the queue until a stop signal is received.
        """
        print("AnimationManager worker thread started.")
        self._is_running = True
        try:
            while not self._stop_event.is_set():
                try:
                    # Get an operation with a timeout to allow checking stop_event
                    row, col, operation = self._operation_queue.get(timeout=0.1)
                except queue.Empty:
                    continue  # No operations, just check stop_event again

                # Get the logical LED object from the matrix
                led_obj = self._led_matrix.get_led(row, col)
                if led_obj is None:
                    print(f"Warning: LED at ({row},{col}) not found in matrix. Skipping operation.")
                    continue

                self._execute_operation(led_obj, operation)
                self._operation_queue.task_done()

        except Exception as e:
            print(f"AnimationManager worker thread encountered an error: {e}")
        finally:
            self._is_running = False
            print("AnimationManager worker thread stopped.")

    def _execute_operation(self, led_obj: ILED, operation: LEDOperation):
        """
        Executes a single LEDOperation on a logical LED, applying changes
        to the matrix and refreshing the physical display.
        """
        current_time = time.monotonic()
        # Wait until the operation's start_time
        if operation.start_time > current_time:
            wait_time = operation.start_time - current_time
            if wait_time > 0:
                time.sleep(wait_time)

        # Get current brightness (from the logical LED, which syncs with controller)
        start_brightness_float = led_obj.brightness

        # Convert target_brightness (0-255) to float (0.0-1.0)
        target_brightness_float = operation.target_brightness / BRIGHTNESS_MAX

        # --- Ramp Up ---
        if operation.ramp_duration > 0:
            self._animate_brightness(led_obj, start_brightness_float, target_brightness_float, operation.ramp_duration)
        else:
            # If no ramp, jump directly to target brightness
            led_obj.brightness = target_brightness_float
            self._pixel_controller.set_pixel(led_obj.row, led_obj.col, *led_obj.color, led_obj.brightness)
            self._pixel_controller.show()

        # --- Hold ---
        if operation.hold_duration > 0 and not self._stop_event.is_set():
            # Ensure LED is at target brightness for hold
            led_obj.brightness = target_brightness_float
            self._pixel_controller.set_pixel(led_obj.row, led_obj.col, *led_obj.color, led_obj.brightness)
            self._pixel_controller.show()  # Ensure state is visible

            time.sleep(operation.hold_duration)

        # --- Fade Down ---
        if operation.fade_duration > 0 and not self._stop_event.is_set():
            self._animate_brightness(led_obj, target_brightness_float, BRIGHTNESS_MIN / BRIGHTNESS_MAX,
                                     operation.fade_duration)
        else:
            # If no fade, turn off directly
            led_obj.off()
            self._pixel_controller.set_pixel(led_obj.row, led_obj.col, *led_obj.color, led_obj.brightness)
            self._pixel_controller.show()

        # Ensure LED is off if it should be after the operation, and stop event wasn't set
        if not self._stop_event.is_set():
            led_obj.off()
            self._pixel_controller.set_pixel(led_obj.row, led_obj.col, *led_obj.color, led_obj.brightness)
            self._pixel_controller.show()

    def _animate_brightness(self, led_obj: ILED, start_b_float: float, end_b_float: float, duration: float,
                            steps: int = 50):
        """
        Smoothly animates the LED's brightness from start to end over a duration.
        Updates the logical LED and calls the pixel controller to render.
        """
        if duration <= 0 or steps <= 0:
            # If duration is 0 or less, just jump to the end brightness
            led_obj.brightness = end_b_float
            self._pixel_controller.set_pixel(led_obj.row, led_obj.col, *led_obj.color, led_obj.brightness)
            self._pixel_controller.show()
            return

        step_delay = duration / steps
        for i in range(steps + 1):
            if self._stop_event.is_set():
                break

            current_b_float = start_b_float + (end_b_float - start_b_float) * (i / steps)
            led_obj.brightness = current_b_float
            # Update the specific pixel on the controller
            self._pixel_controller.set_pixel(led_obj.row, led_obj.col, *led_obj.color, led_obj.brightness)
            self._pixel_controller.show()  # Show the current state

            time.sleep(step_delay)

    def add_operation(self, row: int, col: int, operation: LEDOperation):
        """
        Adds an LED operation for a specific pixel to the queue.
        Starts the worker thread if it's not already running.
        """
        if not (0 <= row < self._led_matrix.rows and 0 <= col < self._led_matrix.cols):
            print(f"Warning: Attempted to add operation for out-of-bounds pixel ({row},{col}). Skipping.")
            return

        self._operation_queue.put((row, col, operation))
        self._start_worker_thread()
        # print(f"AnimationManager: Added operation for ({row},{col}). Queue size: {self._operation_queue.qsize()}") # Debug

    def apply_pattern_commands(self, pattern_generator: Generator[Tuple[Tuple[int, int], LEDOperation], None, None]):
        """
        Takes a pattern generator that yields ((row, col), LEDOperation) tuples
        and adds them to the manager's operation queue.
        """
        print("AnimationManager: Applying pattern commands from generator...")
        commands_applied = 0
        for (row, col), operation in pattern_generator:
            self.add_operation(row, col, operation)
            commands_applied += 1
        print(f"AnimationManager: Applied {commands_applied} pattern commands to queue.")

    def start(self):
        """Starts the animation manager's worker thread."""
        self._start_worker_thread()
        print("AnimationManager: Started.")

    def stop(self):
        """
        Stops the animation manager's worker thread, clears its queue,
        and ensures all LEDs are turned off via the pixel controller.
        """
        if self._is_running:
            print("AnimationManager: Stopping worker thread...")
            self._stop_event.set()  # Signal thread to stop
            if self._worker_thread:
                self._worker_thread.join(timeout=2.0)  # Wait for thread to finish
                if self._worker_thread.is_alive():
                    print("Warning: AnimationManager thread did not stop gracefully.")
            self._is_running = False
            self._worker_thread = None  # Clear thread object

        # Clear any remaining commands in the queue
        with self._operation_queue.mutex:
            self._operation_queue.queue.clear()

        # Ensure physical LEDs are off after stopping
        self._pixel_controller.clear()
        print("AnimationManager: Stopped and all LEDs cleared.")

    def clear_pending_operations(self):
        """Clears all operations currently in the queue for this manager."""
        with self._operation_queue.mutex:
            self._operation_queue.queue.clear()
        print("AnimationManager: All pending operations cleared from queue.")

    def _start_worker_thread(self):
        """Internal method to start the worker thread if it's not running."""
        if not self._is_running and (self._worker_thread is None or not self._worker_thread.is_alive()):
            self._stop_event.clear()  # Clear any previous stop signal
            self._worker_thread = threading.Thread(target=self._worker_thread_main, name="AnimationManagerWorker")
            self._worker_thread.daemon = True  # Allow main program to exit even if thread is running
            self._worker_thread.start()