# src/bongo/app.py
import os
import sys
import time
import logging

# --- Setup Python Path ---
# This ensures that the script can find all project modules when run.
# It assumes app.py is in src/bongo/ and the root is two levels up.
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
config_path = os.path.join(project_root, 'config')
if config_path not in sys.path:
    sys.path.insert(0, config_path)

# --- Project Imports ---
from bongo.hardware_manager import HardwareManager
from bongo.matrix.matrix import LEDMatrix
from config.loader import ConfigLoader
from bongo.utils.logger import setup_logging
from bongo.operations.animation_manager import AnimationManager
# Import a pattern to demonstrate running an animation
# from bongo.patterns.base_patterns import create_wave_pattern

# --- Constants ---
PRODUCTION_CONFIG_PATH = os.path.join(project_root, "config", "production_config.json")


def main():
    """Main application entry point for the Bongo LED system."""

    # 1. Load configuration to get logging settings first.
    try:
        loader = ConfigLoader()
        loader.load_from_file(PRODUCTION_CONFIG_PATH)
        logging_config = loader.get_logging_config()
    except Exception as e:
        print(f"FATAL ERROR: Could not load configuration file at '{PRODUCTION_CONFIG_PATH}': {e}")
        sys.exit(1)

    # 2. Setup logging for the entire application.
    setup_logging(logging_config)
    log = logging.getLogger("bongo.app")

    log.info("🚀 Bongo Application Starting...")

    # 3. Get the full LED configuration.
    try:
        full_led_config = loader.get_led_config()

        # Filter for PCA9685 LEDs and map keys for the matrix.
        # The main application should handle all LED types defined in the config.
        # For now, we are focusing on initializing the PCA9685-based matrix.
        pca_led_config = []
        for item in full_led_config:
            if item.get("type") == "pca9685":
                new_item = item.copy()
                if 'address' in new_item: new_item['controller_address'] = new_item.pop('address')
                if 'pin' in new_item: new_item['led_channel'] = new_item.pop('pin')
                pca_led_config.append(new_item)

        if not pca_led_config:
            log.warning("No LEDs of type 'pca9685' found in the configuration. No matrix created.")
            # Depending on desired behavior, we could exit or continue if there are other LED types.
            # For now, we will assume the PCA matrix is essential.
            return

        controller_addresses = list(set(item['controller_address'] for item in pca_led_config))
        log.info(f"Found {len(pca_led_config)} PCA9685 LEDs and {len(controller_addresses)} unique controllers.")

    except Exception as e:
        log.critical("FATAL ERROR: Could not parse LED configuration.", exc_info=True)
        return

    # 4. Initialize hardware and create the matrix.
    try:
        hw_manager = HardwareManager(addresses=controller_addresses)
        matrix = LEDMatrix(config=pca_led_config, hardware_manager=hw_manager)
        log.info(f"Hardware initialized. Matrix created with {matrix.rows} rows and {matrix.cols} columns.")
    except Exception as e:
        log.critical("FATAL ERROR: Could not initialize hardware or create matrix.", exc_info=True)
        log.info("Tip: Check I2C connections and run 'i2cdetect -y 1' on the Pi.")
        return

    # 5. Initialize the AnimationManager with the live matrix.
    animation_manager = AnimationManager(matrix=matrix)
    log.info("AnimationManager initialized.")

    # --- Example: Load and run a startup pattern ---
    log.info("Loading startup 'wave' pattern...")
    # Get all coordinates of the configured LEDs to pass to the pattern
    all_led_coords = list(matrix.leds.keys())
    # wave_pattern = create_wave_pattern(all_led_coords, start_time_base=time.monotonic())
    # for coords, pixel_op in wave_pattern:
    #     animation_manager.add_operation(coords[0], coords[1], pixel_op)
    # log.info("Startup pattern loaded into AnimationManager.")

    # 6. Start the main application loop.
    log.info("Entering main loop... (Ctrl+C to exit)")
    try:
        while True:
            # The tick method advances all animations by one step.
            animation_manager.tick()
            # The sleep duration determines the frame rate of the animations.
            time.sleep(1 / 60)  # Aim for ~60 FPS

    except KeyboardInterrupt:
        print()  # Newline after ^C
        log.info("Caught Ctrl+C. Initiating shutdown sequence.")
    finally:
        # 7. Gracefully shut down the hardware.
        if 'matrix' in locals():
            log.info("Shutting down matrix and turning off all LEDs...")
            matrix.shutdown()
            log.info("✅ Shutdown complete.")


if __name__ == "__main__":
    main()
