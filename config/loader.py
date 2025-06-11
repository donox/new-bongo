# config/loader.py
import json
from typing import Dict, List, Any

class ConfigLoader:
    """Handles loading of the matrix hardware configuration."""

    def __init__(self, config_data: Dict[str, Any] = None):
        """
        Initializes the loader, optionally with pre-existing config data.
        """
        self._config = config_data if config_data else {}

    def load_from_file(self, filepath: str) -> None:
        """
        Loads the hardware configuration from a JSON file.

        Args:
            filepath: The path to the JSON configuration file.
        """
        try:
            with open(filepath, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            # Handle error appropriately
            print(f"Error: Configuration file not found at {filepath}")
            raise
        except json.JSONDecodeError:
            # Handle error appropriately
            print(f"Error: Could not decode JSON from {filepath}")
            raise

    def get_led_config(self) -> List[Dict[str, Any]]:
        """
        Returns the 'leds' part of the configuration.
        """
        return self._config.get('leds', [])

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Returns the 'logging' section of the configuration.
        Returns an empty dictionary if it's not present.
        """
        return self._config.get('logging', {})

