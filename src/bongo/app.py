# In src/bongo/app.py
import time
from config.loader import ConfigLoader
from src.bongo.matrix.matrix import LEDMatrix
from src.bongo.operations.animation_manager import AnimationManager
# Import the real hardware class for production
from src.bongo.hardware.pca9685_hal import PCA9685

# --- Constants ---
PRODUCTION_CONFIG_PATH = "config/production_config.json"

def main():
    """Main application entry point."""
    print("🚀 Bongo is starting up...")

    # 1. Load the configuration
    print(f"Loading production configuration from: {PRODUCTION_CONFIG_PATH}")
    loader = ConfigLoader()
    loader.load_from_file(PRODUCTION_CONFIG_PATH)
    led_config = loader.get_led_config()

    if not led_config:
        print("Configuration is empty or invalid. Exiting.")
        return

    # 2. Create the LEDMatrix instance (the factory)
    # The matrix is now the single, authoritative object for all LED control.
    print("Initializing LED Matrix...")
    matrix = LEDMatrix(
        config=led_config,
        default_pca9685_class=PCA9685 # Provide the REAL hardware class for production
    )

    # 3. Initialize the AnimationManager with the real matrix
    print("Initializing Animation Manager...")
    animation_manager = AnimationManager(matrix=matrix)

    # 4. Run patterns, animations, etc.
    #    (Your application's main loop would go here)
    # --- Example Usage ---
    # from src.bongo.patterns.base_patterns import create_wave_pattern
    # pattern = create_wave_pattern(list(matrix.leds.keys())) # Get all coords from the matrix
    # for coords, op in pattern:
    #     animation_manager.add_operation(coords[0], coords[1], op)

    print("Entering main loop (Ctrl+C to exit)...")
    try:
        while True:
            animation_manager.tick()
            time.sleep(0.01) # Main loop delay
    except KeyboardInterrupt:
        print("\nShutting down...")
        matrix.shutdown()
        print("Bongo has shut down gracefully.")

if __name__ == "__main__":
    main()