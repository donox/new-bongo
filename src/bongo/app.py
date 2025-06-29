# src/bongo/app.py
import os
import sys
import time
import logging
from bongo.patterns.builtin_patterns import create_fade_all_pattern

# --- Setup Python Path ---
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

# --- Constants ---
PRODUCTION_CONFIG_PATH = os.path.join(project_root, "config", "production_config.json")


def main():
    """Main application entry point for the Bongo LED system."""

    # 1-4. [Previous initialization code remains the same]
    try:
        loader = ConfigLoader()
        loader.load_from_file(PRODUCTION_CONFIG_PATH)
        logging_config = loader.get_logging_config()
    except Exception as e:
        print(f"FATAL ERROR: Could not load configuration file at '{PRODUCTION_CONFIG_PATH}': {e}")
        sys.exit(1)

    setup_logging(logging_config)
    log = logging.getLogger("bongo.app")
    log.info("🚀 Bongo Application Starting...")

    try:
        full_led_config = loader.get_led_config()
        pca_led_config = []
        for item in full_led_config:
            if item.get("type") == "pca9685":
                new_item = item.copy()
                if 'address' in new_item: new_item['controller_address'] = new_item.pop('address')
                if 'pin' in new_item: new_item['led_channel'] = new_item.pop('pin')
                pca_led_config.append(new_item)

        if not pca_led_config:
            log.warning("No LEDs of type 'pca9685' found in the configuration.")
            return

        controller_addresses = list(set(item['controller_address'] for item in pca_led_config))
        log.info(f"Found {len(pca_led_config)} PCA9685 LEDs and {len(controller_addresses)} unique controllers.")

    except Exception as e:
        log.critical("FATAL ERROR: Could not parse LED configuration.", exc_info=True)
        return

    try:
        hw_manager = HardwareManager(addresses=controller_addresses)
        matrix = LEDMatrix(config=pca_led_config, hardware_manager=hw_manager)
        log.info(f"Hardware initialized. Matrix created with {matrix.rows} rows and {matrix.cols} columns.")
    except Exception as e:
        log.critical("FATAL ERROR: Could not initialize hardware or create matrix.", exc_info=True)
        return

    # 5. Initialize the AnimationManager
    animation_manager = AnimationManager(matrix=matrix)
    log.info("AnimationManager initialized.")



    # # 6. Create and load a simple test pattern
    # log.info("Creating simple test pattern...")
    #
    # all_led_coords = list(matrix.leds.keys())
    # log.info(f"Found {len(all_led_coords)} LED coordinates: {all_led_coords[:5]}...")
    #
    # if all_led_coords:
    #     test_coords = all_led_coords[0]
    #     log.info(f"Testing with LED at coordinates: {test_coords}")
    #
    #     # Create operation that starts AFTER we enter the main loop
    #     start_time = time.monotonic() + 1.0  # Start 1 second from now
    #
    #     from bongo.operations.led_operation import LEDPixelOperation
    #
    #     # Create the operation directly to ensure correct initial_brightness
    #     pixel_op = LEDPixelOperation(
    #         target_brightness=1.0,
    #         ramp_duration=3.0,
    #         hold_duration=2.0,
    #         fade_duration=3.0,
    #         start_time=start_time,
    #         initial_brightness=0.0  # Start from OFF
    #     )
    #
    #     log.info(f"Created operation: {pixel_op}")
    #     animation_manager.add_operation(test_coords[0], test_coords[1], pixel_op)
    #     log.info("Operation loaded - will start in 1 second")
    #     # Create operation that starts immediately
    #
    # else:
    #     log.error("No LED coordinates found!")
    #     return
    # 6. Test faster chase with all LEDs
    log.info("Loading faster chase with all LEDs...")

    all_led_coords = list(matrix.leds.keys())

    if all_led_coords:
        from bongo.patterns.builtin_patterns import create_chase_pattern

        # Use all LEDs but with faster timing
        delay_between_leds = 0.2  # 200ms between LEDs (faster than 1s)
        hold_time = 0.3  # 300ms hold time

        # Calculate cycle timing
        cycle_duration = len(all_led_coords) * delay_between_leds + hold_time + 0.08
        gap_duration = 0.5
        total_cycle_time = cycle_duration + gap_duration

        log.info(f"Using {len(all_led_coords)} LEDs with {delay_between_leds}s delays")
        log.info(f"Each cycle: ~{cycle_duration:.1f}s, total with gap: ~{total_cycle_time:.1f}s")

        # 6. Simple chase with immediate timing
        log.info("Loading simple immediate chase...")

        all_led_coords = list(matrix.leds.keys())
        test_coords = all_led_coords[:16]                 # !!!!!!!!!!!!!!!!!!!!!!!!!!!! remove subsetting

        if test_coords:
            from bongo.patterns.builtin_patterns import create_chase_pattern

            # Start very soon with moderate timing
            chase_ops = create_chase_pattern(
                led_coords=test_coords,
                delay=0.3,  # 300ms delays - moderate speed
                brightness=0.8,
                hold_time=0.4,
                start_time_base=time.monotonic() + 0.5  # Start in just 0.5 seconds
            )

            for coords, pixel_op in chase_ops:
                animation_manager.add_operation(coords[0], coords[1], pixel_op)

            log.info(f"Loaded {len(chase_ops)} operations, starting in 0.5 seconds")

        else:
            log.error("No LED coordinates found!")
            return

    # Debug: Check what operations are loaded
    # log.info(f"Total operations loaded: {len(animation_manager.operations)}")
    # if animation_manager.operations:
    #     first_op = animation_manager.operations[0]
    #     log.info(f"First operation starts at: {first_op.pixel_op.start_time}")
    #     log.info(f"Current time: {time.monotonic()}")
    #     log.info(f"Time until first operation: {first_op.pixel_op.start_time - time.monotonic():.2f}s")


    # 7. Start the main application loop.
    log.info("Entering main loop...")
    try:
        frame_count = 0
        while True:
            animation_manager.tick()

            # Much less frequent logging to reduce overhead
            if frame_count % 600 == 0:  # Every 10 seconds instead of 5
                active_ops = len(animation_manager.operations)
                log.info(f"Frame {frame_count}: {active_ops} active operations")
                print(f"Frame {frame_count}: {active_ops} active operations")       # !!!!!!!!!!!!!!!!

            frame_count += 1
            time.sleep(1 / 60)

    except KeyboardInterrupt:
        print()  # Newline after ^C
        log.info("Caught Ctrl+C. Initiating shutdown sequence.")
    finally:
        # 8. Gracefully shut down the hardware.
        if 'matrix' in locals():
            log.info("Shutting down matrix and turning off all LEDs...")
            matrix.shutdown()
            log.info("✅ Shutdown complete.")

if __name__ == "__main__":
    main()