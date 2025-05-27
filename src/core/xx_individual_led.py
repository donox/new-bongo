"""
xx_individual_led.py
Defines the IndividualLED class, which manages a single AbstractLED instance,
its state, and its command queue. Each IndividualLED runs in its own thread.
"""

import time
import threading
import queue

from bongo.interfaces.hardware import IPixelController
from src.core.led_commands import LEDOperation, BRIGHTNESS_MIN

class IndividualLED:
    """
    Represents a single conceptual LED, managing its own state and command queue.
    Each IndividualLED runs in a dedicated thread to process its operations.
    """
    def __init__(self, hw_led: AbstractLED, led_id: str):
        if not isinstance(hw_led, AbstractLED):
            raise TypeError("hw_led must be an instance of AbstractLED.")

        self._hw_led = hw_led  # The actual hardware-controlling LED object
        self.led_id = led_id   # Unique identifier for this LED

        self._command_queue = queue.Queue() # Queue of LEDOperation objects
        self._thread = None
        self._stop_event = threading.Event()
        self._is_running = False

        self._hw_led.off() # Ensure physical LED is off initially
        # No _current_brightness stored here, as it's managed by hw_led now

    def _animate_brightness(self, start_b: int, end_b: int, duration: float, steps: int = 50):
        """
        Smoothly animates the LED's brightness from start_b to end_b over a duration.
        Uses hw_led.set_brightness().
        """
        if duration <= 0 or steps <= 0:
            self._hw_led.set_brightness(end_b)
            return

        step_interval = duration / steps
        for i in range(steps + 1):
            if self._stop_event.is_set():
                return # Stop animation if signal received

            current_b = int(start_b + (end_b - start_b) * (i / steps))
            self._hw_led.set_brightness(current_b)
            self._stop_event.wait(step_interval) # Use wait to be responsive to stop event

    def _execute_operation(self, operation: LEDOperation):
        """
        Executes a single LEDOperation (wait for t0, ramp, hold, fade).
        """
        current_time = time.monotonic()

        # Phase 1: Wait until start_time (t0)
        if operation.start_time > current_time:
            time_to_wait = operation.start_time - current_time
            # print(f"LED {self.led_id}: Waiting {time_to_wait:.2f}s until start_time.") # Debug
            self._stop_event.wait(time_to_wait)
            if self._stop_event.is_set(): return

        # Get current actual brightness from the hardware LED for smooth transitions
        start_brightness = self._hw_led.get_brightness()

        # Phase 2: Ramp up (t1)
        if operation.ramp_duration > 0:
            # print(f"LED {self.led_id}: Ramping from {start_brightness} to {operation.target_brightness} over {operation.ramp_duration:.2f}s.") # Debug
            self._animate_brightness(start_brightness, operation.target_brightness, operation.ramp_duration)
            if self._stop_event.is_set(): return
        else: # Instant set if no ramp
            self._hw_led.set_brightness(operation.target_brightness)

        # Phase 3: Hold (t2)
        if operation.hold_duration > 0:
            # print(f"LED {self.led_id}: Holding at {operation.target_brightness} for {operation.hold_duration:.2f}s.") # Debug
            self._stop_event.wait(operation.hold_duration)
            if self._stop_event.is_set(): return

        # Phase 4: Fade off (t3)
        if operation.fade_duration > 0:
            # print(f"LED {self.led_id}: Fading from {self._hw_led.get_brightness()} to {BRIGHTNESS_MIN} over {operation.fade_duration:.2f}s.") # Debug
            self._animate_brightness(self._hw_led.get_brightness(), BRIGHTNESS_MIN, operation.fade_duration)
            if self._stop_event.is_set(): return
        else: # Instant off if no fade
            self._hw_led.off()

    def _worker_thread(self):
        """Thread function that continuously processes operations from the queue."""
        while not self._stop_event.is_set():
            try:
                operation = self._command_queue.get(timeout=0.1) # Small timeout to check stop_event
                # print(f"LED {self.led_id}: Processing operation: {operation}") # Debug
                self._execute_operation(operation)
                self._command_queue.task_done()
            except queue.Empty:
                continue # No operations, just keep checking stop_event
            except Exception as e:
                print(f"Error in LED {self.led_id} worker thread: {e}")
                # Log error, decide whether to continue or stop thread

    def add_operation(self, operation: LEDOperation):
        """Adds a single LED operation to this LED's command queue."""
        self._command_queue.put(operation)
        if not self._is_running:
            self.start()

    def start(self):
        """Starts the dedicated processing thread for this LED."""
        if not self._is_running:
            self._is_running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._worker_thread, name=f"LED-{self.led_id}-Worker")
            self._thread.daemon = True # Allows main program to exit even if threads are running
            self._thread.start()
            # print(f"LED {self.led_id} worker thread started.") # Debug

    def stop(self):
        """
        Stops the dedicated thread for this LED, clears its queue, and turns the LED off.
        """
        if self._is_running:
            # print(f"Stopping LED {self.led_id} worker thread...") # Debug
            self._stop_event.set() # Signal thread to stop
            self._thread.join(timeout=1.0) # Wait for thread to finish, with a timeout
            if self._thread.is_alive():
                print(f"Warning: LED {self.led_id} thread did not stop gracefully.")
            self._is_running = False
            # Clear any remaining commands if stopping
            with self._command_queue.mutex:
                self._command_queue.queue.clear()
            self._hw_led.off() # Ensure physical LED is off
            # print(f"LED {self.led_id} thread stopped.") # Debug

    def clear_pending_operations(self):
        """Clears all operations currently in the queue for this LED."""
        with self._command_queue.mutex:
            self._command_queue.queue.clear()
        print(f"LED {self.led_id}: Pending operations cleared.")

    def get_current_brightness(self) -> int:
        """Returns the current brightness of the underlying hardware LED."""
        return self._hw_led.get_brightness()