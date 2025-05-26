# integration/test_rpi_gpio_led.py

import unittest
import time
import os
import sys

# # --- Start Diagnostic Code ---
# print("\n--- Diagnostic Check ---")
# # Adjust this path if your 'lights' project root is different on the Pi
# # This path should point to the directory that *contains* 'src'
# project_root_for_diag = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
# src_path_for_diag = os.path.join(project_root_for_diag, 'src')
# hardware_path_for_diag = os.path.join(src_path_for_diag, 'hardware')
#
# print(f"Calculated project root for diag: '{project_root_for_diag}'")
# print(f"Calculated src path for diag: '{src_path_for_diag}'")
# print(f"sys.path currently contains: {sys.path}")
#
#
# def print_dir_contents(path, label=""):
#     print(f"Checking {label} contents of '{path}':")
#     if not os.path.exists(path):
#         print(f"  ERROR: Path does NOT exist!")
#         return
#     if not os.path.isdir(path):
#         print(f"  ERROR: Path is NOT a directory!")
#         return
#     try:
#         contents = os.listdir(path)
#         print(f"  Contents: {contents}")
#     except OSError as e:
#         print(f"  ERROR: Could not list contents: {e}")
#
#
# def check_init_file(path_to_dir):
#     init_file = os.path.join(path_to_dir, '__init__.py')
#     print(f"  Checking '{init_file}':")
#     if os.path.exists(init_file):
#         print(f"    Exists: YES")
#         try:
#             with open(init_file, 'r') as f:
#                 content_snippet = f.read(50)  # Read first 50 chars
#             print(f"    Snippet (first 50 chars): '{content_snippet.strip()}' (length: {len(content_snippet.strip())})")
#             if not content_snippet.strip():
#                 print(
#                     "    WARNING: __init__.py seems empty or contains only whitespace. This is usually fine, but check for hidden characters.")
#         except Exception as e:
#             print(f"    ERROR: Could not read file content: {e}")
#     else:
#         print(f"    Exists: NO (This is often the problem for 'No module named X' when X is a directory on sys.path)")
#
#
# print_dir_contents(src_path_for_diag, label="'src'")
# check_init_file(src_path_for_diag)
#
# print_dir_contents(hardware_path_for_diag, label="'src/hardware'")
# check_init_file(hardware_path_for_diag)
#
# # Check for the specific module file
# pi_pwm_led_file = os.path.join(hardware_path_for_diag, 'rpi_gpio_hal.py')
# print(f"Checking '{pi_pwm_led_file}':")
# if os.path.exists(pi_pwm_led_file):
#     print(f"  Exists: YES")
#     try:
#         with open(pi_pwm_led_file, 'r') as f:
#             content_snippet = f.read(50)
#         print(f"  Snippet (first 50 chars): '{content_snippet.strip()}'")
#     except Exception as e:
#         print(f"  ERROR: Could not read file content: {e}")
# else:
#     print(f"  Exists: NO")
#
# print("--- End Diagnostic Check ---\n")
# # --- End Diagnostic Code ---


# Importantly, DO NOT mock RPi.GPIO here. We want the real one.
# Ensure sys.path is correctly configured by run_integration_tests.py

try:
    import RPi.GPIO as GPIO
    from bongo.hardware.rpi_gpio_hal import PiPWMLED, cleanup_pi_pwm, _pwm_objects

    GPIO_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    GPIO_AVAILABLE = False
    print(f"Skipping PiPWMLED integration tests: RPi.GPIO not available or setup issue: {e}")
    print(f"DEBUG: Import error details: {e}")  # More verbose error
    print(f"DEBUG: Attempting to import 'src.hardware.pi_pwm_led' failed. sys.path: {sys.path}")


@unittest.skipUnless(GPIO_AVAILABLE, "RPi.GPIO not available for actual hardware testing.")
class TestPiPWMLEDIntegration(unittest.TestCase):
    # Recommend using a GPIO pin that supports hardware PWM if possible,
    # or a known working software PWM pin. GPIO18 is a common choice.
    GPIO_PIN = 18  # Change this to your actual LED pin

    def setUp(self):
        print(f"\n--- Setting up PiPWMLED test on GPIO{self.GPIO_PIN} ---")
        # Ensure GPIO is clean before each test
        cleanup_pi_pwm()
        GPIO.setmode(GPIO.BCM)  # Use BCM numbering
        GPIO.setup(self.GPIO_PIN, GPIO.OUT)
        self.led = PiPWMLED("integration_pi_led", self.GPIO_PIN)
        print(f"LED should be OFF initially on GPIO{self.GPIO_PIN}.")
        time.sleep(0.1)  # Give hardware a moment

    def tearDown(self):
        print(f"--- Tearing down PiPWMLED test on GPIO{self.GPIO_PIN} ---")
        self.led.off()
        cleanup_pi_pwm()  # Always clean up GPIO
        print(f"LED should be OFF after tearDown on GPIO{self.GPIO_PIN}.")
        time.sleep(0.1)  # Give hardware a moment

    def test_initial_state_off(self):
        # Visually confirm LED is off.
        # Can't programmatically assert physical state without extra hardware,
        # so this is more a visual confirmation test.
        print("Test: Initial state (should be OFF)")
        self.assertEqual(self.led.get_brightness(), 0)  # Should be 0 internally

    def test_set_brightness_visible(self):
        print("Test: Setting brightness to 100 (should be visibly dim)")
        self.led.set_brightness(100)
        time.sleep(1)  # Allow time for visual confirmation
        self.assertEqual(self.led.get_brightness(), 100)

        print("Test: Setting brightness to 255 (should be visibly bright)")
        self.led.set_brightness(255)
        time.sleep(1)  # Allow time for visual confirmation
        self.assertEqual(self.led.get_brightness(), 255)

        print("Test: Setting brightness to 0 (should be OFF)")
        self.led.set_brightness(0)
        time.sleep(1)  # Allow time for visual confirmation
        self.assertEqual(self.led.get_brightness(), 0)

    def test_off_method(self):
        print("Test: Setting brightness to 150, then calling off() (should turn OFF)")
        self.led.set_brightness(150)
        time.sleep(0.5)
        self.led.off()
        time.sleep(0.5)
        self.assertEqual(self.led.get_brightness(), 0)

    def test_brightness_clamping(self):
        print("Test: Setting brightness above 255 (should clamp to 255)")
        self.led.set_brightness(300)  # Should clamp to 255
        time.sleep(0.5)
        self.assertEqual(self.led.get_brightness(), 255)

        print("Test: Setting brightness below 0 (should clamp to 0)")
        self.led.set_brightness(-50)  # Should clamp to 0
        time.sleep(0.5)
        self.assertEqual(self.led.get_brightness(), 0)

    def test_individual_led_with_pi_pwm(self):
        # This tests the integration of IndividualLED with actual PiPWMLED
        print("Test: IndividualLED with PiPWMLED (should animate smoothly)")
        from src.core.individual_led import IndividualLED
        from src.core.led_commands import LEDOperation, BRIGHTNESS_MAX, BRIGHTNESS_MIN

        individual_led = IndividualLED(self.led, "complex_pi_led")  # Use the actual PiPWMLED instance

        # Operation: Ramp up, hold, fade off
        op = LEDOperation(
            start_time=time.monotonic() + 0.5,  # Start half a second from now
            target_brightness=BRIGHTNESS_MAX,
            ramp_duration=1.0,
            hold_duration=0.5,
            fade_duration=1.0
        )
        individual_led.add_operation(op)

        # Allow sufficient time for the operation to complete
        total_op_duration = op.ramp_duration + op.hold_duration + op.fade_duration + (op.start_time - time.monotonic())
        print(f"Waiting {total_op_duration:.2f}s for LED animation.")
        time.sleep(total_op_duration + 0.5)  # Add a small buffer

        # Assert final state (should be off after fade)
        self.assertEqual(self.led.get_brightness(), BRIGHTNESS_MIN)

        # Stop the thread to ensure cleanup
        individual_led.stop()
        self.assertFalse(individual_led._is_running)


# To run this file directly for debugging:
if __name__ == '__main__':
    # Ensure sys.path is correct for imports if running directly
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming run_integration_tests.py is in integration/, and src/ is sibling to integration/
    # This means project root (lights/) is one level up from integration/
    project_root = os.path.abspath(os.path.join(current_script_dir, os.pardir))
    src_directory = os.path.abspath(os.path.join(project_root, 'src'))

    if src_directory not in sys.path:
        sys.path.insert(0, src_directory)

    # Run the tests
    unittest.main()