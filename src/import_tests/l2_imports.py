import sys
try:
    print("ONE", flush=True)
    import RPi.GPIO as GPIO
    print("TWO", flush=True)
    from src.hardware.pi_pwm_led import PiPWMLED, cleanup_pi_pwm, _pwm_objects
    print("THREE", flush=True)
    from src.hardware.pca9685_led import PCA9685LED, get_pca9685_board, _pca_boards
    print("FOUR", flush=True)

except (ImportError, RuntimeError) as e:
    print(f"Skipping PiPWMLED integration tests: RPi.GPIO not available or setup issue: {e}")
    print(f"DEBUG: Import error details: {e}")  # More verbose error
    print(f"DEBUG: Attempting to import 'src.hardware.pi_pwm_led' failed. sys.path: {sys.path}")

def make_call():
    print("CALL", flush=True)