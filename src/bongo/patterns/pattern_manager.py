# patterns/pattern_manager.py

import time
import threading
from bongo.patterns import builtin_patterns

class PatternManager:
    def __init__(self, matrix):
        self.matrix = matrix
        self._stop_event = threading.Event()
        self._thread = None

    def run_builtin(self, name: str, **kwargs):
        """Run a named built-in pattern in a separate thread."""
        if hasattr(builtin_patterns, name):
            pattern_func = getattr(builtin_patterns, name)
            self.stop()  # stop any running pattern
            self._stop_event.clear()
            self._thread = threading.Thread(target=pattern_func, args=(self.matrix, self._stop_event), kwargs=kwargs)
            self._thread.start()
        else:
            raise ValueError(f"No built-in pattern named '{name}'")

    def run_steps(self, steps, loop=False):
        """Run custom pattern steps from JSON or code."""
        def step_runner():
            while not self._stop_event.is_set():
                for step in steps:
                    action = step['type']
                    index = step.get('led')
                    row, col = step.get('row'), step.get('col')
                    duration = step.get('duration', 0)

                    if action == 'on':
                        self._on(index, row, col)
                    elif action == 'off':
                        self._off(index, row, col)
                    elif action == 'brightness':
                        value = step.get('value', 1.0)
                        self._brightness(index, row, col, value)

                    time.sleep(duration)

                if not loop:
                    break

        self.stop()
        self._stop_event.clear()
        self._thread = threading.Thread(target=step_runner)
        self._thread.start()

    def _on(self, index, row, col):
        if index is not None:
            self.matrix.on(index)
        elif row is not None and col is not None:
            self.matrix.on_at(row, col)

    def _off(self, index, row, col):
        if index is not None:
            self.matrix.off(index)
        elif row is not None and col is not None:
            self.matrix.off_at(row, col)

    def _brightness(self, index, row, col, value):
        if index is not None:
            self.matrix.set_brightness(index, value)
        elif row is not None and col is not None:
            self.matrix.set_brightness_at(row, col, value)

    def stop(self):
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()
