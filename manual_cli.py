# manual_cli.py
import os
import sys
import time
import logging

# --- Setup Python Path ---
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# --- Imports from your project ---
from bongo.hardware_manager import HardwareManager
from bongo.matrix.matrix import LEDMatrix
from config.loader import ConfigLoader
from bongo.utils.logger import setup_logging

# --- Constants ---
PRODUCTION_CONFIG_PATH = "config/production_config.json"


def main():
    """Main function to run the interactive CLI."""
    try:
        loader = ConfigLoader()
        loader.load_from_file(PRODUCTION_CONFIG_PATH)
        logging_config = loader.get_logging_config()
    except Exception as e:
        print(f"FATAL ERROR: Could not load configuration file at '{PRODUCTION_CONFIG_PATH}': {e}")
        return

    setup_logging(logging_config)
    log = logging.getLogger("bongo.cli")

    log.info("🚀 Bongo Manual Control Interface Starting...")

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
            log.warning("No LEDs of type 'pca9685' found in the configuration file.")
            return

        controller_addresses = list(set(item['controller_address'] for item in pca_led_config))
        log.info(f"Found {len(pca_led_config)} PCA9685 LEDs and {len(controller_addresses)} unique controllers.")

    except Exception as e:
        log.critical("FATAL ERROR: Could not parse LED configuration.", exc_info=True)
        return

    try:
        hw_manager = HardwareManager(addresses=controller_addresses)
    except Exception as e:
        log.critical("FATAL ERROR: Could not initialize hardware.", exc_info=True)
        return

    matrix = LEDMatrix(config=pca_led_config, hardware_manager=hw_manager)
    log.info(f"Hardware initialized. Matrix created with {matrix.rows} rows and {matrix.cols} columns.")
    print("-" * 30)
    print("Enter commands (e.g., 'set 0 2 255' or 'trace on'). Type 'quit' to exit.")

    try:
        while True:
            command_str = input("> ").strip().lower()
            # command_str = "set 0 5 255"
            parts = command_str.split()
            if not parts: continue
            cmd = parts[0]

            if cmd in ["quit", "exit"]: break

            try:
                if cmd == "set" and len(parts) == 4:
                    row, col, brightness = map(int, parts[1:])
                    log.info(f"CLI: Received command to set LED ({row}, {col}) to brightness {brightness}.")
                    matrix.set_pixel(row, col, brightness)
                elif cmd == "fill" and len(parts) == 2:
                    brightness = int(parts[1])
                    log.info(f"CLI: Received command to fill all LEDs with brightness {brightness}.")
                    matrix.fill(brightness)
                elif cmd == "clear":
                    log.info("CLI: Received command to clear all LEDs.")
                    matrix.clear()
                elif cmd == "raw" and len(parts) == 3:
                    channel, duty_cycle = map(int, parts[1:])
                    log.info(f"CLI: Sending RAW command: Channel={channel}, Duty Cycle={duty_cycle}...")
                    pca_controller = hw_manager.get_controller(controller_addresses[0])
                    pca_controller.channels[channel].duty_cycle = duty_cycle
                    log.info("CLI: Raw command sent.")
                elif cmd == "trace" and len(parts) == 2:
                    level = logging.DEBUG if parts[1] == "on" else logging.INFO
                    logging.getLogger("bongo").setLevel(level)
                    log.info(f"Trace logging set to {parts[1].upper()}.")
                else:
                    print(f"Unknown command or wrong arguments: '{command_str}'")
            except ValueError:
                print("Invalid number. Row, column, and brightness must be integers.")
            except Exception as e:
                log.error("An error occurred while executing command:", exc_info=True)

    except KeyboardInterrupt:
        print("\nCaught Ctrl+C.")
    finally:
        log.info("Shutting down matrix and turning off all LEDs...")
        matrix.shutdown()
        log.info("✅ Shutdown complete.")


if __name__ == "__main__":
    main()
